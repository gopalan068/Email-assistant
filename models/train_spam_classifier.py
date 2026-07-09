"""
train_spam_classifier.py
========================
Retrain the spam classifier using three combined datasets:
  1. Enron Spam       – loaded from HuggingFace (SetFit/enron_spam)
  2. SpamAssassin     – auto-downloaded from Apache mirror
  3. TREC 2007        – pre-cleaned CSV (default: D:/learn/processed_data.csv)

Usage:
    # Use default TREC path
    python train_spam_classifier.py

    # Override TREC path
    python train_spam_classifier.py --trec07 "C:/path/to/processed_data.csv"

    # Skip TREC (train on Enron + SpamAssassin only)
    python train_spam_classifier.py --skip-trec
"""

import os
import re
import sys
import io
import tarfile
import argparse
import urllib.request
import joblib
import numpy as np
import pandas as pd
import scipy.sparse as sp

from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    precision_score,
    recall_score,
    roc_auc_score,
    confusion_matrix,
)

# ---------------------------------------------------------------------------
# SpamAssassin public corpus files
# ---------------------------------------------------------------------------
SPAMASSASSIN_BASE = "https://spamassassin.apache.org/old/publiccorpus"
SPAMASSASSIN_FILES = [
    ("20021010_easy_ham.tar.bz2",  0),   # ham
    ("20021010_hard_ham.tar.bz2",  0),   # ham
    ("20021010_spam.tar.bz2",      1),   # spam
    ("20030228_easy_ham.tar.bz2",  0),   # ham
    ("20030228_easy_ham_2.tar.bz2",0),   # ham
    ("20030228_hard_ham.tar.bz2",  0),   # ham
    ("20030228_spam.tar.bz2",      1),   # spam
    ("20030228_spam_2.tar.bz2",    1),   # spam
    ("20050311_spam_2.tar.bz2",    1),   # spam
]

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_sa_cache")


# ---------------------------------------------------------------------------
# Feature engineering helpers
# ---------------------------------------------------------------------------
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)

def _count_urls(text: str) -> int:
    """Count the number of URLs in text."""
    return len(URL_RE.findall(text))

def _uppercase_ratio(text: str) -> float:
    """Fraction of alphabetic characters that are uppercase."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if c.isupper()) / len(letters)

def _special_char_count(text: str) -> int:
    """Count spam-indicator characters: ! $ ? #"""
    return sum(text.count(c) for c in "!$?#")

def _is_reply(subject: str) -> int:
    """1 if the subject starts with Re: / RE: / Fwd: etc."""
    s = (subject or "").strip().lower()
    return 1 if s.startswith(("re:", "re :", "fwd:", "fw:")) else 0

def _has_unsubscribe(text: str) -> int:
    """1 if the body contains an unsubscribe link/phrase (newsletter signal → ham)."""
    t = text.lower()
    return 1 if ("unsubscribe" in t or "opt-out" in t or "opt out" in t) else 0

def build_extra_features(subjects: pd.Series, bodies: pd.Series) -> np.ndarray:
    """
    Build a (N, 5) numeric feature matrix from subject + body columns.
    Features:
        0: URL count in body
        1: Uppercase ratio in subject
        2: Special char count in body (!$?#)
        3: Is-reply flag
        4: Has-unsubscribe flag
    """
    n = len(subjects)
    feats = np.zeros((n, 5), dtype=np.float32)
    for i, (subj, body) in enumerate(zip(subjects, bodies)):
        subj = subj or ""
        body = body or ""
        feats[i, 0] = _count_urls(body)
        feats[i, 1] = _uppercase_ratio(subj)
        feats[i, 2] = _special_char_count(body)
        feats[i, 3] = _is_reply(subj)
        feats[i, 4] = _has_unsubscribe(body)
    return feats


# ---------------------------------------------------------------------------
# Dataset loaders
# ---------------------------------------------------------------------------
def load_enron() -> pd.DataFrame:
    """Load the Enron spam dataset from HuggingFace."""
    print("\n[1/3] Loading Enron dataset from HuggingFace ...")
    try:
        ds = load_dataset("SetFit/enron_spam")
    except Exception as e:
        print(f"  ERROR: {e}")
        return pd.DataFrame(columns=["subject", "body", "label"])

    frames = []
    for split in ds:
        df = pd.DataFrame(ds[split])
        text_col = "text" if "text" in df.columns else "message"
        subj_col = "subject" if "subject" in df.columns else None

        # Enron dataset has 'subject' and 'text' (or 'message') columns
        if subj_col and subj_col in df.columns:
            frames.append(pd.DataFrame({
                "subject": df[subj_col].fillna(""),
                "body":    df[text_col].fillna(""),
                "label":   df["label"],
            }))
        else:
            # Fallback: treat full text as body, no subject
            frames.append(pd.DataFrame({
                "subject": "",
                "body":    df[text_col].fillna(""),
                "label":   df["label"],
            }))

    result = pd.concat(frames, ignore_index=True)
    print(f"  Loaded {len(result):,} emails  "
          f"(spam={result['label'].sum():,}, ham={(result['label']==0).sum():,})")
    return result


def _parse_raw_email(raw_bytes: bytes) -> tuple[str, str]:
    """
    Parse raw RFC-2822 email bytes.
    Returns (subject, body_text).
    """
    import email as email_lib
    try:
        msg = email_lib.message_from_bytes(raw_bytes)
    except Exception:
        return "", raw_bytes.decode("utf-8", errors="replace")

    subject = msg.get("Subject", "") or ""

    body_parts = []
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/plain":
                try:
                    body_parts.append(part.get_payload(decode=True).decode("utf-8", errors="replace"))
                except Exception:
                    pass
        if not body_parts:
            # fallback: grab first part payload as string
            for part in msg.walk():
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body_parts.append(payload.decode("utf-8", errors="replace"))
                        break
                except Exception:
                    pass
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                body_parts.append(payload.decode("utf-8", errors="replace"))
        except Exception:
            body_parts.append(str(msg.get_payload()))

    body = "\n".join(body_parts)
    # Strip HTML tags if present
    body = re.sub(r"<[^>]+>", " ", body)
    body = re.sub(r"\s+", " ", body).strip()
    return subject, body


def _download_spamassassin(filename: str) -> bytes | None:
    """Download a SpamAssassin corpus file, using a local cache."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, filename)
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return f.read()
    url = f"{SPAMASSASSIN_BASE}/{filename}"
    print(f"    Downloading {filename} ...", end=" ", flush=True)
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            data = resp.read()
        with open(cache_path, "wb") as f:
            f.write(data)
        print(f"OK ({len(data) // 1024} KB)")
        return data
    except Exception as e:
        print(f"FAILED ({e})")
        return None


def load_spamassassin() -> pd.DataFrame:
    """Auto-download and parse the SpamAssassin public corpus."""
    print("\n[2/3] Loading SpamAssassin public corpus ...")
    rows = []
    for filename, label in SPAMASSASSIN_FILES:
        data = _download_spamassassin(filename)
        if data is None:
            continue
        try:
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:bz2") as tar:
                members = [m for m in tar.getmembers() if m.isfile()]
                for member in members:
                    # Skip CMDS / index files
                    if os.path.basename(member.name) in ("cmds", "index"):
                        continue
                    try:
                        raw = tar.extractfile(member).read()
                        subject, body = _parse_raw_email(raw)
                        rows.append({"subject": subject, "body": body, "label": label})
                    except Exception:
                        pass
        except Exception as e:
            print(f"  ERROR parsing {filename}: {e}")

    result = pd.DataFrame(rows)
    print(f"  Loaded {len(result):,} emails  "
          f"(spam={result['label'].sum():,}, ham={(result['label']==0).sum():,})")
    return result


def load_trec07(csv_path: str) -> pd.DataFrame:
    """
    Load the pre-cleaned TREC 2007 CSV.
    Expected columns: label, subject, email_to, email_from, message
    label: 0=ham, 1=spam
    """
    print(f"\n[3/3] Loading TREC 2007 from CSV: {csv_path} ...")
    if not os.path.exists(csv_path):
        print(f"  WARNING: File not found — skipping TREC 2007.")
        return pd.DataFrame(columns=["subject", "body", "label"])

    df = pd.read_csv(csv_path, low_memory=False)

    # Normalize column names (lowercase)
    df.columns = [c.lower().strip() for c in df.columns]

    subject_col = "subject" if "subject" in df.columns else None
    body_col    = "message" if "message" in df.columns else "body"
    label_col   = "label"

    result = pd.DataFrame({
        "subject": df[subject_col].fillna("") if subject_col else "",
        "body":    df[body_col].fillna(""),
        "label":   df[label_col].astype(int),
    })

    print(f"  Loaded {len(result):,} emails  "
          f"(spam={result['label'].sum():,}, ham={(result['label']==0).sum():,})")
    return result


# ---------------------------------------------------------------------------
# Training pipeline
# ---------------------------------------------------------------------------
def train_classifier(trec07_path: str, skip_trec: bool = False):
    # ── Load datasets ────────────────────────────────────────────────────────
    enron = load_enron()
    sa    = load_spamassassin()
    trec  = pd.DataFrame(columns=["subject", "body", "label"]) if skip_trec else load_trec07(trec07_path)

    all_data = pd.concat([enron, sa, trec], ignore_index=True)
    all_data = all_data.dropna(subset=["label"])
    all_data["label"]   = all_data["label"].astype(int)
    # Force plain str — prevents Header/object type errors from email parsers
    all_data["subject"] = all_data["subject"].fillna("").astype(str)
    all_data["body"]    = all_data["body"].fillna("").astype(str)

    print(f"\n{'='*55}")
    print(f"  Combined dataset: {len(all_data):,} emails")
    print(f"  Spam : {all_data['label'].sum():,}")
    print(f"  Ham  : {(all_data['label'] == 0).sum():,}")
    print(f"{'='*55}")

    # ── Build combined text for TF-IDF ──────────────────────────────────────
    # Format mirrors exactly what spam_filter.py sends at inference time:
    #   "Subject: {subject}\n\n{body}"
    tfidf_input = "Subject: " + all_data["subject"] + "\n\n" + all_data["body"]

    # ── Build extra numeric features ────────────────────────────────────────
    print("\nBuilding feature-engineered columns ...")
    extra = build_extra_features(all_data["subject"], all_data["body"])
    print(f"  Extra feature matrix shape: {extra.shape}")

    # ── Train / test split ──────────────────────────────────────────────────
    X_text_train, X_text_test, \
    X_extra_train, X_extra_test, \
    y_train, y_test = train_test_split(
        tfidf_input, extra, all_data["label"],
        test_size=0.15, random_state=42, stratify=all_data["label"]
    )

    # ── TF-IDF vectorization ─────────────────────────────────────────────────
    print("\nVectorizing text using TF-IDF ...")
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=20_000,      # increased from 10k
        ngram_range=(1, 2),
        sublinear_tf=True,        # log-scale TF → less weight to very frequent terms
        min_df=2,                 # ignore terms seen in only 1 document
    )
    X_train_tfidf = vectorizer.fit_transform(X_text_train)
    X_test_tfidf  = vectorizer.transform(X_text_test)

    # Combine TF-IDF + extra numeric features
    X_train = sp.hstack([X_train_tfidf, sp.csr_matrix(X_extra_train)], format="csr")
    X_test  = sp.hstack([X_test_tfidf,  sp.csr_matrix(X_extra_test)],  format="csr")

    print(f"  Training matrix: {X_train.shape}")

    # ── Train Logistic Regression ────────────────────────────────────────────
    print("\nTraining Logistic Regression ...")
    # class_weight={0: 1.2, 1: 1.0} → slightly penalise false ham->spam calls
    # (less aggressive than the old {0:1.5, 1:1.0}, since more data makes the
    #  model naturally more precise; we want to recover some recall now)
    model = LogisticRegression(
        C=0.5,
        class_weight={0: 1.2, 1: 1.0},
        max_iter=1000,
        solver="lbfgs",
    )
    model.fit(X_train, y_train)

    # ── Evaluation ───────────────────────────────────────────────────────────
    y_pred      = model.predict(X_test)
    y_prob_spam = model.predict_proba(X_test)[:, 1]

    print("\n" + "="*55)
    print("EVALUATION RESULTS")
    print("="*55)
    print(classification_report(y_test, y_pred, target_names=["Ham", "Spam"]))

    spam_precision = precision_score(y_test, y_pred, pos_label=1)
    spam_recall    = recall_score(y_test, y_pred, pos_label=1)
    auc            = roc_auc_score(y_test, y_prob_spam)
    cm             = confusion_matrix(y_test, y_pred)

    print(f"Spam Precision : {spam_precision:.4f}   (fewer false positives = better)")
    print(f"Spam Recall    : {spam_recall:.4f}   (fewer missed spams = better)")
    print(f"AUC-ROC        : {auc:.4f}")
    print(f"\nConfusion Matrix:")
    print(f"              Predicted Ham  Predicted Spam")
    print(f"  Actual Ham  {cm[0][0]:>13,}  {cm[0][1]:>13,}")
    print(f"  Actual Spam {cm[1][0]:>13,}  {cm[1][1]:>13,}")
    print("="*55)

    # ── Save model ───────────────────────────────────────────────────────────
    models_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(models_dir, "spam_classifier.pkl")

    joblib.dump({
        "model":      model,
        "vectorizer": vectorizer,
        # Flag so spam_filter.py knows to also build extra features
        "has_extra_features": True,
    }, model_path)

    size_kb = os.path.getsize(model_path) // 1024
    print(f"\nModel saved -> {model_path}  ({size_kb:,} KB)")
    print("Done.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrain spam classifier")
    parser.add_argument(
        "--trec07",
        default="D:/learn/processed_data.csv",
        help="Path to the pre-cleaned TREC 2007 CSV file (default: D:/learn/processed_data.csv)",
    )
    parser.add_argument(
        "--skip-trec",
        action="store_true",
        help="Skip TREC 2007 dataset (train on Enron + SpamAssassin only)",
    )
    args = parser.parse_args()
    train_classifier(trec07_path=args.trec07, skip_trec=args.skip_trec)
