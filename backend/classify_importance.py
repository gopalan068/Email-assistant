import json
import os
import re

# Safely import ML packages
try:
    import joblib
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    HAS_ML = True
except ImportError:
    HAS_ML = False

from .llm_client import call_llm

# ---------------------------------------------------------------------------
# TRANSACTIONAL DOMAIN WHITELIST
# Emails from these senders are always "transactional/important", never newsletter.
# ---------------------------------------------------------------------------
TRANSACTIONAL_DOMAINS = [
    "bankofindia.co.in", "sbi.co.in", "hdfcbank.com", "icicibank.com",
    "axisbank.com", "kotak.com", "yesbank.in", "pnbindia.in",
    "canarabank.com", "unionbankofindia.co.in", "bankofbaroda.in",
    "federalbank.co.in", "idfcfirstbank.com", "indusind.com",
    "paytm.com", "phonepe.com", "razorpay.com", "billdesk.com",
    "amazon.com", "amazon.in", "flipkart.com",
    "irctc.co.in", "maketrip.com", "goibibo.com",
    "bluedart.com", "delhivery.com", "shiprocket.in",
    "incometax.gov.in", "gst.gov.in", "uidai.gov.in",
]

# ---------------------------------------------------------------------------
# SERVICE / BRAND SENDER PATTERNS  (these are NOT personal senders)
# If the from_name or from_email matches these, the email is not from a person.
# ---------------------------------------------------------------------------
SERVICE_NAME_PATTERNS = [
    "no-reply", "noreply", "newsletter", "notification", "notifications",
    "digest", "update", "updates", "support", "team", "info", "service",
    "alert", "alerts", "mailer", "auto", "automated", "do-not-reply",
    "donotreply", "marketing", "offers", "promo", "deals", "news",
    "billing", "accounts", "system", "postmaster", "webmaster",
    "announce", "announcement", "broadcast", "campaign",
    # Transactional / auth service patterns (common in OTP/security mails)
    "registration", "signup", "sign-up", "verify", "verification",
    "confirm", "activate", "activation", "security", "admin", "contact",
    "hello", "welcome", "member", "account", "password", "reset",
]


def _extract_domain(email_addr: str) -> str:
    """Extracts bare domain from an email address."""
    if "@" in email_addr:
        return email_addr.lower().split("@")[-1].strip(" >").split("/")[0]
    return ""


def is_transactional_sender(email_data) -> bool:
    """Returns True if sender is a known transactional institution (bank, courier, etc.)."""
    domain = _extract_domain(email_data.get("from_email", ""))
    return any(domain == td or domain.endswith("." + td) for td in TRANSACTIONAL_DOMAINS)


def is_personal_sender(email_data) -> bool:
    """
    Returns True when the email appears to come from a real human being.
    A personal sender has:
    - A non-service from_name (no keywords like 'team', 'noreply', 'support')
    - A non-service from_email local part (not 'info@', 'noreply@', etc.)
    - Does NOT have a List-Unsubscribe header
    """
    from_name = email_data.get("from_name", "").lower()
    from_email = email_data.get("from_email", "").lower()
    list_unsubscribe = email_data.get("list_unsubscribe", "")

    # Must not have List-Unsubscribe header (newsletters / automated mail always have it)
    if list_unsubscribe and list_unsubscribe.strip():
        return False

    # Check sender name and local-part of email for service patterns
    local_part = from_email.split("@")[0] if "@" in from_email else from_email
    combined = from_name + " " + local_part

    if any(pat in combined for pat in SERVICE_NAME_PATTERNS):
        return False

    # A personal name usually has a space (First Last) or looks like a name
    # At minimum, the from_name must be non-empty
    if not from_name.strip():
        return False

    return True


def is_newsletter_heuristic(email_data) -> bool:
    """
    Returns True only when MULTIPLE signals confirm this is a newsletter/automated update.
    Requires 2+ signals to fire (previously any single signal was enough, causing
    transactional bank emails with List-Unsubscribe to be mis-tagged as newsletters).
    """
    # Transactional senders are NEVER newsletters regardless of headers
    if is_transactional_sender(email_data):
        return False

    sender_email = email_data.get("from_email", "").lower()
    sender_name = email_data.get("from_name", "").lower()
    body = email_data.get("body", "").lower()
    list_unsubscribe = email_data.get("list_unsubscribe", "")

    score = 0

    # Signal 1: Has List-Unsubscribe header
    if list_unsubscribe and len(list_unsubscribe.strip()) > 0:
        score += 1

    # Signal 2: Sender email contains newsletter/notification indicator
    email_indicators = [
        "no-reply", "noreply", "newsletter", "notification", "digest",
        "updates", "news", "mailer", "announce", "broadcast", "campaign",
    ]
    if any(ind in sender_email for ind in email_indicators):
        score += 1

    # Signal 3: Sender name contains notification indicator
    name_indicators = [
        "newsletter", "notification", "digest", "updates", "team",
        "mailer", "weekly", "daily", "bulletin",
    ]
    if any(ind in sender_name for ind in name_indicators):
        score += 1

    # Signal 4: Body contains unsubscribe links/words
    if "unsubscribe" in body or "view in browser" in body or "opt out" in body:
        score += 1

    # Signal 5: Personal sender → definitely NOT a newsletter
    if is_personal_sender(email_data):
        return False

    # Require at least 2 signals to classify as newsletter
    return score >= 2


def get_email_preview(email) -> str:
    """Safely extracts a 500-character snippet of the email body."""
    snippet = email.get("snippet", "")
    body = email.get("body", "")
    preview_text = snippet if snippet else body
    if not preview_text:
        preview_text = "No content."
    preview_text = " ".join(preview_text.split())
    return preview_text[:500]


def has_whole_word(text: str, keyword: str) -> bool:
    """Checks if a keyword exists as a whole word in the text, avoiding partial matches."""
    pattern = r'\b' + re.escape(keyword) + r'\b'
    return bool(re.search(pattern, text, re.IGNORECASE))


def extract_signals(email):
    """
    Extracts structured binary signals from an email for use by the ML pre-filter
    and as context hints sent to the LLM.
    Feature order (11 dimensions):
      [is_thread_reply, has_finance_kw, has_work_kw, has_health_kw, has_urgent_kw,
       is_vip_sender, is_newsletter, has_otp_kw, has_security_kw, has_career_kw, has_order_kw]
    """
    subject = email.get("subject", "").lower()
    body = email.get("body", "").lower()
    sender_email = email.get("from_email", "").lower()
    sender_name = email.get("from_name", "").lower()
    list_unsubscribe = email.get("list_unsubscribe", "")

    is_thread_reply = subject.startswith("re:") or subject.startswith("fwd:")

    fin_keywords = [
        "invoice", "payment", "bank", "credit", "debit", "repayment",
        "emi", "transaction", "billing", "receipt", "statement", "salary",
    ]
    has_finance_keywords = any(
        has_whole_word(subject, k) or has_whole_word(body, k) for k in fin_keywords
    )

    work_keywords = [
        "review", "slides", "deck", "meeting", "sync", "project", "client",
        "schedule", "deadline", "urgency", "tasks", "action items",
        "onboarding", "joining", "resignation",
    ]
    has_work_keywords = any(
        has_whole_word(subject, k) or has_whole_word(body, k) for k in work_keywords
    )

    health_keywords = [
        "appointment", "dentist", "doctor", "clinic", "checkup", "medical",
        "prescription", "lab report", "test result", "hospital",
    ]
    has_health_keywords = any(
        has_whole_word(subject, k) or has_whole_word(body, k) for k in health_keywords
    )

    urgent_keywords = [
        "urgent", "immediate", "action required", "critical", "important",
        "asap", "due today", "reminder", "last date", "expiring",
        "verification required", "confirm your", "declined", "decline",
        "failed", "failure", "cancelled", "cancel", "suspended", "suspension",
        "overdue", "unpaid", "bounced",
    ]
    has_urgent_keywords = any(
        has_whole_word(subject, k) or has_whole_word(body, k) for k in urgent_keywords
    )

    # Dynamic VIP sender: emails from a personal sender (human, not a bot/brand)
    is_vip_sender = (
        is_personal_sender(email) or
        is_transactional_sender(email)
    )

    is_newsletter = (
        len(list_unsubscribe.strip()) > 0 or
        any(
            ind in sender_email
            for ind in ["no-reply", "noreply", "newsletter", "notification", "digest", "update", "news", "info@"]
        ) or
        "unsubscribe" in body or
        "view in browser" in body or
        "opt out" in body
    )

    # ── New category-specific signals ────────────────────────────────────────
    otp_kw = [
        "otp", "one-time password", "one time password", "verification code",
        "your code", "login code", "access code", "auth code", "confirm code","code","request to log in",
    ]
    has_otp_keywords = any(has_whole_word(subject, k) or has_whole_word(body, k) for k in otp_kw)

    security_kw = [
        "password reset", "security alert", "login attempt", "suspicious login",
        "suspicious activity", "unusual activity", "new device", "new sign-in",
        "unauthorized access", "account breach", "two-factor", "2fa",
        "account locked", "account suspended", "security notice",
    ]
    has_security_keywords = any(has_whole_word(subject, k) or has_whole_word(body, k) for k in security_kw)

    career_kw = [
        "offer letter", "job offer", "interview", "job application",
        "application status", "job alert", "career opportunity", "shortlisted",
        "recruiter", "hiring", "internship", "placement", "background check", "joining date",
    ]
    has_career_keywords = any(has_whole_word(subject, k) or has_whole_word(body, k) for k in career_kw)

    order_kw = [
        "order confirmed", "order placed", "order shipped", "your order",
        "shipped", "dispatched", "out for delivery", "delivered",
        "tracking", "return request", "refund initiated",
    ]
    has_order_keywords = any(has_whole_word(subject, k) or has_whole_word(body, k) for k in order_kw)

    return {
        # Core signals (used by ML binary classifier)
        "is_thread_reply":      int(is_thread_reply),
        "has_finance_keywords": int(has_finance_keywords),
        "has_work_keywords":    int(has_work_keywords),
        "has_health_keywords":  int(has_health_keywords),
        "has_urgent_keywords":  int(has_urgent_keywords),
        "is_vip_sender":        int(is_vip_sender),
        "is_newsletter":        int(is_newsletter),
        # Extended category signals (sent as LLM hints; also used by ML)
        "has_otp_keywords":      int(has_otp_keywords),
        "has_security_keywords": int(has_security_keywords),
        "has_career_keywords":   int(has_career_keywords),
        "has_order_keywords":    int(has_order_keywords),
    }


def train_importance_classifier(model_path):
    """
    Trains a LogisticRegression binary importance classifier (important / not-important).
    Feature vector (11 dimensions — must match extract_signals() key order):
      [is_thread_reply, has_finance_kw, has_work_kw, has_health_kw, has_urgent_kw,
       is_vip_sender, is_newsletter, has_otp_kw, has_security_kw, has_career_kw, has_order_kw]
    """
    if not HAS_ML:
        return None
    X = []
    y = []

    # fmt: off
    patterns = [
        # Thread replies → important
        ([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 1),
        ([1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], 1),
        ([1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], 1),
        ([1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0], 1),

        # VIP / personal sender → important
        ([0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], 1),
        ([0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0], 1),
        ([0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0], 1),
        ([0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0], 1),

        # Finance keywords → important
        ([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], 1),
        ([0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0], 1),
        ([0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0], 1),

        # Work keywords → important
        ([0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0], 1),
        ([0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0], 1),

        # Health keywords → important
        ([0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], 1),
        ([0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0], 1),

        # Urgent alone → important
        ([0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0], 1),

        # OTP → always important (time-critical)
        ([0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0], 1),
        ([0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0], 1),

        # Security → always important
        ([0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0], 1),
        ([0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0], 1),

        # Career → important
        ([0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], 1),
        ([0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0], 1),

        # Orders → regular (informational, no action usually needed)
        ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 0),
        ([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1], 0),

        # Newsletters → regular
        ([0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0], 0),
        ([0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0], 0),
        ([0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0], 0),
        ([0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0], 0),
        ([0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0], 0),

        # Plain regular email
        ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0),
        ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0),
        ([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0),
    ]
    # fmt: on

    for feat, label in patterns:
        for _ in range(8):
            X.append(feat)
            y.append(label)

    X = np.array(X)
    y = np.array(y)

    model = LogisticRegression(class_weight="balanced", max_iter=500)
    model.fit(X, y)

    try:
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(model, model_path)
        print(f"[Importance ML] Trained and saved importance classifier to {model_path}")
    except Exception as e:
        print(f"Warning: Failed to save importance classifier: {e}")

    return model


def get_importance_classifier():
    """Loads or trains the LogisticRegression importance classifier."""
    if not HAS_ML:
        return None
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(backend_dir, "..", "models", "importance_classifier.pkl")
    if os.path.exists(model_path):
        try:
            return joblib.load(model_path)
        except Exception as e:
            print(f"Error loading importance model: {e}")

    return train_importance_classifier(model_path)


def determine_ai_status_and_meta(email, reason, is_important):
    """Keyword-based classification taxonomy mapping for display output."""
    subject = email.get("subject", "").lower()
    body = email.get("body", "").lower()
    reason_lower = reason.lower()

    # 1. OTP / Verification Codes (highest specificity — always check first)
    otp_keywords = [
        "otp", "one-time password", "one time password", "verification code",
        "your code", "login code", "access code", "auth code",
        "use code", "enter code", "confirm code", "two-factor code",
        # Sign-up / registration code formats
        "sign up code", "signup code", "sign-up code",
        "is your code", "is your otp",
        "your sign in code", "your signin code", "sign in code","request to log in"
    ]
    if any(has_whole_word(subject, k) or has_whole_word(body, k) for k in otp_keywords):
        return "OTP", "Inbox / OTP"

    # 2. Security Alerts (password resets, suspicious logins, account alerts)
    security_keywords = [
        "password reset", "account security", "login attempt", "sign-in attempt",
        "suspicious login", "suspicious activity", "security alert", "unusual activity",
        "new device", "new sign-in", "unauthorized access", "account breach",
        "two-factor", "2fa", "account locked", "verify your identity",
        "account suspended", "security notice",
    ]
    if any(has_whole_word(subject, k) or has_whole_word(body, k) or has_whole_word(reason_lower, k) for k in security_keywords):
        return "SECURITY ALERT", "Inbox / Security"

    # 3. Jobs / Career
    career_keywords = [
        "offer letter", "job offer", "interview", "job application",
        "application status", "application received", "job alert",
        "career opportunity", "shortlisted", "you have been selected",
        "recruiter", "hiring", "internship", "placement", "campus recruitment",
        "cv review", "background check", "joining date",
    ]
    if any(has_whole_word(subject, k) or has_whole_word(body, k) or has_whole_word(reason_lower, k) for k in career_keywords):
        if is_important:
            return "JOB ALERT", "Inbox / Career"
        else:
            return "CAREER UPDATE", "Inbox / Career"

    # 4. Financial / Payment
    fin_keywords = [
        "invoice", "payment", "bank", "credit", "debit", "repayment",
        "emi", "transaction", "billing", "receipt", "salary", "statement",
    ]
    if any(has_whole_word(subject, k) or has_whole_word(body, k) or has_whole_word(reason_lower, k) for k in fin_keywords):
        if is_important:
            return "PAYMENT INBOUND", "Inbox / Finance"
        else:
            return "TRANSACTIONAL", "Inbox / Finance"

    # 5. Work / Direct Correspondence
    work_keywords = [
        "review", "slides", "deck", "meeting", "sync", "project", "client",
        "schedule", "deadline", "urgency", "tasks", "action items",
        "onboarding",
    ]
    if any(has_whole_word(subject, k) or has_whole_word(body, k) or has_whole_word(reason_lower, k) for k in work_keywords):
        if is_important:
            return "DIRECT CORRESPONDENCE", "Inbox / Work"
        else:
            return "REGULAR", "Inbox / Work"

    # 6. Scheduled Event / Health
    health_keywords = [
        "appointment", "dentist", "doctor", "clinic", "checkup", "medical",
        "prescription", "lab report", "hospital",
    ]
    if any(has_whole_word(subject, k) or has_whole_word(body, k) or has_whole_word(reason_lower, k) for k in health_keywords):
        if is_important:
            return "SCHEDULED EVENT", "Inbox / Health"
        else:
            return "REGULAR", "Inbox / Health"

    # 7. Shopping / Orders
    order_keywords = [
        "order confirmed", "order placed", "order shipped", "your order",
        "shipped", "dispatched", "out for delivery", "delivered", "delivery",
        "tracking", "return request", "refund initiated", "exchange",
    ]
    if any(has_whole_word(subject, k) or has_whole_word(body, k) for k in order_keywords):
        return "ORDER UPDATE", "Inbox / Orders"

    # 8. Social / Networking
    social_keywords = ["linkedin", "facebook", "twitter", "instagram", "connection", "message from", "social"]
    if any(has_whole_word(subject, k) or has_whole_word(body, k) or has_whole_word(reason_lower, k) for k in social_keywords):
        return "SOCIAL ALERTS", "Inbox / Social"

    # 9. Promo / Coupon
    promo_keywords = ["promo", "coupon", "discount", "off next", "sale", "deal", "offer", "cashback"]
    if any(has_whole_word(subject, k) or has_whole_word(body, k) or has_whole_word(reason_lower, k) for k in promo_keywords):
        return "PROMOTIONAL", "Inbox / Promo"

    # 10. Default
    if is_important:
        return "IMPORTANT", "Inbox / Important"
    else:
        return "REGULAR", "Inbox / Regular"


def fallback_importance_classification(email, err_msg=""):
    """Conservative fallback classification in case of LLM API errors."""
    signals = extract_signals(email)
    if (signals["is_thread_reply"] or signals["has_finance_keywords"] or
            signals["has_work_keywords"] or signals["has_health_keywords"] or
            signals["has_urgent_keywords"] or signals["is_vip_sender"]):

        reason = f"Fallback (API Error): Detected urgent or contextual indicators. Error: {err_msg}"
        status, meta = determine_ai_status_and_meta(email, reason, True)
        email["isAiFlagged"] = True
        email["aiStatus"] = status
        email["meta"] = meta
    else:
        reason = f"Fallback (API Error): No urgent indicators found. Error: {err_msg}"
        status, meta = determine_ai_status_and_meta(email, reason, False)
        email["isAiFlagged"] = False
        email["aiStatus"] = status
        email["meta"] = meta


def classify_importance_batch(emails):
    """
    Classifies a list of emails using a 3-tier cascade pipeline:
    Tier 1 (Heuristics) → Tier 2 (ML Pre-filter) → Tier 3 (Batched LLM triage).

    NOTE: Newsletter heuristic is intentionally NOT run here anymore.
    It now runs in api_server.py BEFORE the spam filter, so newsletters
    are correctly routed to digest instead of accidentally hitting the spam ML.
    All emails arriving here are either confirmed non-newsletter or transactional.

    Modifies emails in-place.
    """
    if not emails:
        return emails

    # Load ML Classifier
    ml_model = get_importance_classifier()

    # Emails that need LLM classification (the uncertain middle-ground pool)
    uncertain_emails = []

    for email in emails:
        signals = extract_signals(email)
        subject_lower = email.get("subject", "").lower()

        # ── Tier 1: Fast Heuristics ──────────────────────────────────────────
        # IMPORTANT: OTP and Security are checked FIRST — before thread-reply
        # and VIP-sender — because service senders (e.g. registration@vercel.com)
        # can slip past is_personal_sender() and be mis-routed by Rule B.

        # Rule A: OTP / verification code → always route to OTP section first
        otp_subject_patterns = [
            # Standard OTP words
            "otp", "one-time", "one time", "verification code",
            "your code", "login code", "access code", "auth code", "confirm code",
            # Sign-up / registration code formats (Vercel, GitHub, etc.)
            "sign up code", "signup code", "sign-up code",
            "is your code", "is your otp",
            # Sign-in code formats
            "your sign in code", "your signin code", "sign in code",
            # Common suffixes: "123456 is your X code"
            "is your vercel", "is your google", "is your swiggy",
            "is your amazon", "is your paytm", "is your flipkart","request to log in"
        ]
        if any(pat in subject_lower for pat in otp_subject_patterns):
            email["isAiFlagged"] = True
            email["aiStatus"] = "OTP"
            email["meta"] = "Inbox / OTP"
            continue

        # Rule B: Security alerts → always important, route immediately
        security_subject_patterns = [
            "password reset", "security alert", "login attempt", "suspicious",
            "unauthorized", "account locked", "two-factor", "2fa", "new sign-in",
            "account breach", "security notice", "unusual activity", "verify your identity",
        ]
        if any(pat in subject_lower for pat in security_subject_patterns):
            reason = "Fast Heuristic: Security alert detected in email subject."
            status, meta = determine_ai_status_and_meta(email, reason, True)
            email["isAiFlagged"] = True
            email["aiStatus"] = status
            email["meta"] = meta
            continue

        # Rule C: Career emails → flag as important (interviews, offers are time-sensitive)
        career_subject_patterns = [
            "offer letter", "interview", "job offer", "shortlisted",
            "application status", "you have been selected", "recruiter",
            "joining date", "background check",
        ]
        if any(pat in subject_lower for pat in career_subject_patterns):
            reason = "Fast Heuristic: Career/job email detected in subject."
            status, meta = determine_ai_status_and_meta(email, reason, True)
            email["isAiFlagged"] = True
            email["aiStatus"] = status
            email["meta"] = meta
            continue

        # Rule D: Thread reply is almost always important
        if signals["is_thread_reply"] == 1:
            reason = "Fast Heuristic: Thread reply (Re: or Fwd:) detected."
            status, meta = determine_ai_status_and_meta(email, reason, True)
            email["isAiFlagged"] = True
            email["aiStatus"] = status
            email["meta"] = meta
            continue

        # Rule E: Personal human sender → very likely important
        if signals["is_vip_sender"] == 1:
            reason = "Fast Heuristic: Email from a personal/institutional sender."
            status, meta = determine_ai_status_and_meta(email, reason, True)
            email["isAiFlagged"] = True
            email["aiStatus"] = status
            email["meta"] = meta
            continue

        # Rule F: Urgent keyword in subject → needs attention
        urgent_subject_patterns = [
            "urgent", "action required", "verify", "confirm", "important",
            "reminder", "due", "expires", "last chance", "declined", "decline",
            "failed", "failure", "cancelled", "cancel", "suspended", "suspension",
            "overdue", "unpaid", "bounced",
        ]
        if any(pat in subject_lower for pat in urgent_subject_patterns):
            reason = "Fast Heuristic: Urgency keyword detected in email subject."
            status, meta = determine_ai_status_and_meta(email, reason, True)
            email["isAiFlagged"] = True
            email["aiStatus"] = status
            email["meta"] = meta
            continue

        # ── Tier 2: ML Pre-filter ────────────────────────────────────────────
        # Thresholds lowered from 0.85/0.15 → 0.65/0.35 so the model
        # contributes meaningfully instead of punting everything to the LLM.
        if HAS_ML and ml_model is not None:
            features = [
                signals["is_thread_reply"],
                signals["has_finance_keywords"],
                signals["has_work_keywords"],
                signals["has_health_keywords"],
                signals["has_urgent_keywords"],
                signals["is_vip_sender"],
                signals["is_newsletter"],
                # Extended signals (11-dim model)
                signals["has_otp_keywords"],
                signals["has_security_keywords"],
                signals["has_career_keywords"],
                signals["has_order_keywords"],
            ]
            try:
                prob = ml_model.predict_proba([features])[0][1]

                if prob > 0.65:
                    reason = f"ML Pre-filter: Confident important classification (prob={prob:.2f})."
                    status, meta = determine_ai_status_and_meta(email, reason, True)
                    email["isAiFlagged"] = True
                    email["aiStatus"] = status
                    email["meta"] = meta
                    continue
                elif prob < 0.35:
                    reason = f"ML Pre-filter: Confident regular classification (prob={prob:.2f})."
                    status, meta = determine_ai_status_and_meta(email, reason, False)
                    email["isAiFlagged"] = False
                    email["aiStatus"] = status
                    email["meta"] = meta
                    continue
            except Exception as e:
                print(f"[Importance ML] Prediction error: {e}")

        # If no tier confidently classified this email → queue for LLM
        uncertain_emails.append(email)

    if not uncertain_emails:
        return emails

    # ── Tier 3: Batched LLM Triage ───────────────────────────────────────────
    # Send emails in batches of max 10 to stay within token/parsing limits.
    batch_size = 10

    system_instruction = (
        "You are a professional email triage assistant. For each email, return TWO things:\n"
        "  1. 'importance': 'important' or 'regular'\n"
        "  2. 'category': the single best-matching category string from this fixed list:\n"
        "       otp       — one-time passwords, login codes, verification codes\n"
        "       security  — password resets, suspicious logins, account locked/breach, 2FA alerts\n"
        "       career    — job offers, interview invites, application status, recruiter messages\n"
        "       orders    — order confirmed/shipped, delivery tracking, return/refund status\n"
        "       finance   — bank statements, EMI reminders, invoices, payment receipts, salary\n"
        "       work      — direct messages from colleagues/managers/clients needing a reply\n"
        "       health    — medical appointments, clinic reminders, lab reports\n"
        "       social    — social media notifications (likes, follows, connection requests)\n"
        "       promo     — promotional offers, coupons, discount codes, marketing emails\n"
        "       regular   — everything else that doesn't fit the above\n\n"
        "Rules for 'importance':\n"
        "- Mark 'important' if the email needs the user's direct attention, action, or reply.\n"
        "- otp and security are ALWAYS important.\n"
        "- career emails (interviews, offers) are ALWAYS important.\n"
        "- finance emails like payment declines, payment failures, subscription cancellations, or bill dues are ALWAYS important because they require immediate user action.\n"
        "- orders are usually 'regular' (informational); mark important only if action is needed (e.g. failed delivery).\n"
        "- When in doubt, lean toward 'important'.\n\n"
        "  3. 'reason': one concise sentence explaining your classification.\n\n"
        "Return a JSON object keyed by email ID. Example:\n"
        "{\n"
        "  \"msg_101\": {\"importance\": \"important\", \"category\": \"security\",  \"reason\": \"Password reset link sent to account.\"},\n"
        "  \"msg_102\": {\"importance\": \"important\", \"category\": \"otp\",      \"reason\": \"Contains a one-time login code.\"},\n"
        "  \"msg_103\": {\"importance\": \"important\", \"category\": \"career\",   \"reason\": \"Interview invitation from recruiter.\"},\n"
        "  \"msg_104\": {\"importance\": \"regular\",   \"category\": \"orders\",   \"reason\": \"Shipping update, no action needed.\"},\n"
        "  \"msg_105\": {\"importance\": \"regular\",   \"category\": \"promo\",    \"reason\": \"Promotional discount offer.\"}\n"
        "}"
    )

    for i in range(0, len(uncertain_emails), batch_size):
        batch = uncertain_emails[i:i + batch_size]

        batch_input = []
        for email in batch:
            batch_input.append({
                "id": email["id"],
                "sender": f"{email.get('from_name', '')} <{email.get('from_email', '')}>",
                "subject": email.get("subject", ""),
                "preview": get_email_preview(email),
                "signals": extract_signals(email),
            })

        prompt = (
            "Classify the following emails. Return results as a JSON object keyed by email ID.\n\n"
            f"Emails:\n{json.dumps(batch_input, indent=2)}"
        )

        try:
            print(f"[LLM Triage] Calling LLM for batch of {len(batch)} emails...")
            response_text = call_llm(prompt, system_instruction=system_instruction, json_mode=True)
            results = json.loads(response_text)

            for email in batch:
                msg_id = email["id"]
                classification = results.get(msg_id, {})
                importance_str = classification.get("importance", "regular").lower()
                category_str   = classification.get("category", "").lower().strip()
                reason         = classification.get("reason", "")

                is_important = (importance_str == "important")

                # If LLM returned a valid category, use it for direct section routing.
                # This is more reliable than keyword matching when the body is ambiguous.
                CATEGORY_MAP = {
                    "otp":      ("OTP",              "Inbox / OTP",    True),
                    "security": ("SECURITY ALERT",   "Inbox / Security", True),
                    "career":   ("JOB ALERT" if is_important else "CAREER UPDATE", "Inbox / Career", is_important),
                    "orders":   ("ORDER UPDATE",     "Inbox / Orders",  False),
                    "finance":  ("PAYMENT INBOUND" if is_important else "TRANSACTIONAL", "Inbox / Finance", is_important),
                    "work":     ("DIRECT CORRESPONDENCE" if is_important else "REGULAR", "Inbox / Work", is_important),
                    "health":   ("SCHEDULED EVENT" if is_important else "REGULAR", "Inbox / Health", is_important),
                    "social":   ("SOCIAL ALERTS",   "Inbox / Social",  False),
                    "promo":    ("PROMOTIONAL",      "Inbox / Promo",   False),
                }

                if category_str in CATEGORY_MAP:
                    ai_status, meta, flagged = CATEGORY_MAP[category_str]
                    email["isAiFlagged"] = flagged
                    email["aiStatus"]   = ai_status
                    email["meta"]       = meta
                else:
                    # LLM didn't return a known category — fall back to keyword matching
                    status, meta = determine_ai_status_and_meta(email, reason, is_important)
                    email["isAiFlagged"] = is_important
                    email["aiStatus"]   = status
                    email["meta"]       = meta

        except Exception as e:
            print(f"[LLM Triage] Error during batch classification: {e}. Falling back to heuristics.")
            for email in batch:
                fallback_importance_classification(email, err_msg=str(e))

    return emails
