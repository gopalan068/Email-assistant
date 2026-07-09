import os
import re
import joblib
import numpy as np
import scipy.sparse as sp

# ---------------------------------------------------------------------------
# TRUSTED SENDER WHITELIST
# Emails from these domains/patterns ALWAYS bypass the spam ML model.
# They are known legitimate senders (banks, couriers, major platforms).
# ---------------------------------------------------------------------------
TRUSTED_DOMAINS = [
    # Indian Banks & Finance
    "bankofindia.co.in", "sbi.co.in", "hdfcbank.com", "icicibank.com",
    "axisbank.com", "kotak.com", "yesbank.in", "pnbindia.in",
    "canarabank.com", "unionbankofindia.co.in", "bankofbaroda.in",
    "federalbank.co.in", "idfcfirstbank.com", "indusind.com",
    # Payments & Wallets
    "paytm.com", "phonepe.com", "googlepay.com", "razorpay.com",
    "billdesk.com", "ccavenue.com", "amazonpay.com",
    # E-commerce & Delivery
    "amazon.com", "amazon.in", "flipkart.com", "myntra.com",
    "meesho.com", "nykaa.com", "snapdeal.com",
    "bluedart.com", "delhivery.com", "ekart.com", "shiprocket.in",
    # Services & Utilities
    "irctc.co.in", "maketrip.com", "goibibo.com", "cleartrip.com",
    "zomato.com", "swiggy.in", "blinkit.com",
    "linkedin.com", "google.com", "microsoft.com", "apple.com",
    "github.com", "gitlab.com", "slack.com", "zoom.us",
    # Government / Tax
    "incometax.gov.in", "gst.gov.in", "uidai.gov.in",
]

# Sub-string patterns in the domain that indicate a trusted institutional sender
TRUSTED_DOMAIN_PATTERNS = [
    "bank", "gov.in", "hospital", "clinic", "edu", "university",
    "school", "college", "insurance", "mutual", "finance",
]

# ---------------------------------------------------------------------------
# Feature engineering helpers (must mirror train_spam_classifier.py exactly)
# ---------------------------------------------------------------------------
_URL_RE = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)

def _count_urls(text: str) -> int:
    return len(_URL_RE.findall(text))

def _uppercase_ratio(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if c.isupper()) / len(letters)

def _special_char_count(text: str) -> int:
    return sum(text.count(c) for c in "!$?#")

def _is_reply(subject: str) -> int:
    s = (subject or "").strip().lower()
    return 1 if s.startswith(("re:", "re :", "fwd:", "fw:")) else 0

def _has_unsubscribe(text: str) -> int:
    t = text.lower()
    return 1 if ("unsubscribe" in t or "opt-out" in t or "opt out" in t) else 0

def _build_extra_features(subject: str, body: str) -> np.ndarray:
    """Build the same 5-feature numeric vector used during training."""
    return np.array([[  
        _count_urls(body),
        _uppercase_ratio(subject),
        _special_char_count(body),
        _is_reply(subject),
        _has_unsubscribe(body),
    ]], dtype=np.float32)


class SpamFilter:
    def __init__(self, model_path=None):
        if model_path is None:
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(backend_dir, "..", "models", "spam_classifier.pkl")
            
        self.model_path = os.path.abspath(model_path)
        self.model = None
        self.vectorizer = None
        self.has_extra_features = False
        # Probability threshold: model must be ≥80% confident to call it spam.
        # This dramatically reduces false positives on transactional emails.
        self.spam_threshold = 0.80
        self.load_model()
        
    def load_model(self):
        if not os.path.exists(self.model_path):
            print(f"Warning: Spam classifier model file not found at {self.model_path}. Fallback to heuristics-only mode.")
            return
        try:
            data = joblib.load(self.model_path)
            self.model = data["model"]
            self.vectorizer = data["vectorizer"]
            # New models include engineered features; old models do not
            self.has_extra_features = data.get("has_extra_features", False)
            print(f"Loaded spam classifier model from {self.model_path} "
                  f"(extra_features={self.has_extra_features})")
        except Exception as e:
            print(f"Error loading spam classifier: {e}")

    def _extract_domain(self, sender: str) -> str:
        """Extracts the bare domain from a sender string like 'Name <user@domain.com>'."""
        sender_lower = sender.lower()
        if "@" in sender_lower:
            parts = sender_lower.split("@")
            if len(parts) > 1:
                return parts[1].strip(" >").split("/")[0].split("?")[0]
        return ""

    def _is_trusted_sender(self, sender: str) -> bool:
        """
        Returns True if the sender domain is in the trusted whitelist.
        Trusted senders ALWAYS bypass the spam ML model.
        """
        domain = self._extract_domain(sender)
        if not domain:
            return False
        # Exact match against known trusted domains
        if any(domain == td or domain.endswith("." + td) for td in TRUSTED_DOMAINS):
            return True
        # Pattern match for institutional domains (ensuring full-word boundary matches to avoid false positives like 'w3schools')
        for pattern in TRUSTED_DOMAIN_PATTERNS:
            if "." in pattern or pattern in ["edu", "gov"]:
                if domain.endswith(pattern) or domain.endswith("." + pattern):
                    return True
            else:
                parts = domain.replace("-", ".").split(".")
                if any(part == pattern for part in parts):
                    return True
        return False

    def is_spam(self, subject: str, sender: str, body: str) -> bool:
        """
        Returns True only if the email is very likely spam.

        Pipeline:
        1. Trusted-sender whitelist (bypass → not spam)
        2. Hard-block heuristics (known spam TLDs, blocked domains, blocked patterns)
        3. ML model with high-confidence threshold (≥ 0.80 probability required)
        """
        sender_lower = sender.lower()

        # ── Step 1: Trusted sender whitelist ────────────────────────────────
        if self._is_trusted_sender(sender):
            print(f"[Spam Whitelist] Trusted sender, skipping ML: {sender}")
            return False

        # ── Step 2: Hard-block heuristics ───────────────────────────────────
        # 2a. Blocklisted TLDs (common spam/phishing registrar zones)
        spam_tlds = [
            ".xyz", ".click", ".win", ".top", ".link", ".download",
            ".account", ".club", ".bid", ".loan", ".gq", ".tk", ".ml",
            ".cf", ".ga", ".buzz", ".cyou", ".rest", ".casa", ".cfd",
        ]
        domain = self._extract_domain(sender)
        if domain and any(domain.endswith(tld) for tld in spam_tlds):
            print(f"[Spam Heuristic] Blocked sender due to spam TLD: {sender}")
            return True

        # 2b. Blocklisted domains (known scam/phishing sites)
        spam_domains = [
            "lottery.xyz", "winbiglottery.xyz", "cheapmeds-discount.net",
            "scam-pharmacy.net", "winbig.lottery", "phishing-link.com",
            "suspicious-link-to-steal-your-identity.xyz",
            "discover.pinterest.com","ideas.pinterest.com",
        ]
        if any(dom in sender_lower for dom in spam_domains):
            print(f"[Spam Heuristic] Blocked sender from blocklisted domain: {sender}")
            return True

        # 2c. Blocklisted sender name/display-name patterns
        spam_name_patterns = [
            "win grand prize", "claims-department", "cheapmeds",
            "lottery claims", "claim your award", "you have won",
            "congratulations winner","ServiceNow"
        ]
        if any(pat in sender_lower for pat in spam_name_patterns):
            print(f"[Spam Heuristic] Blocked sender based on display-name pattern: {sender}")
            return True

        # ── Step 3: ML model with high-confidence threshold ─────────────────
        if self.model is None or self.vectorizer is None:
            # No model loaded — be conservative, trust the email
            return False

        text = f"Subject: {subject}\n\n{body}"
        try:
            tfidf_vec = self.vectorizer.transform([text])

            if self.has_extra_features:
                # Append the 5 engineered numeric features (same as training)
                extra = _build_extra_features(subject, body)
                vec = sp.hstack([tfidf_vec, sp.csr_matrix(extra)], format="csr")
            else:
                vec = tfidf_vec

            # Use probability instead of hard prediction to control false positives
            spam_prob = self.model.predict_proba(vec)[0][1]
            is_spam_result = spam_prob >= self.spam_threshold
            if is_spam_result:
                print(f"[Spam ML] Classified as SPAM (prob={spam_prob:.3f} ≥ {self.spam_threshold}): {subject[:60]}")
            else:
                print(f"[Spam ML] Classified as HAM (prob={spam_prob:.3f} < {self.spam_threshold}): {subject[:60]}")
            return is_spam_result
        except Exception as e:
            print(f"Error predicting spam probability: {e}")
            return False
