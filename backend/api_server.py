import os
import sys
import json
import hashlib
import time
import re
import threading
import requests
from flask import Flask, jsonify, request

# Ensure backend directory is in python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(backend_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Load env variables before importing local modules
from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, ".env"))

from backend.spam_filter import SpamFilter
from backend.fetch_emails import fetch_recent_emails
from backend.classify_importance import classify_importance_batch
from backend.generate_digest import generate_newsletter_digest
from backend.llm_client import call_llm

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
if not GOOGLE_CLIENT_ID:
    raise ValueError("GOOGLE_CLIENT_ID environment variable is not set. Please set it in your .env file.")

# Token Cache structure: { hash: (email, cache_expiry) }
token_verif_cache = {}

def verify_token_and_get_email(token):
    if not token:
        print("[Debug Auth] No token provided in the Authorization header!")
        return None
    
    if token.startswith("mock_token_"):
        return token.replace("mock_token_", "") + "@gmail.com"
        
    # Use token hash as key to avoid storing raw token in memory structures
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    now = time.time()
    
    # Opportunistic cleanup to prevent memory leaks
    if len(token_verif_cache) > 100:
        expired_keys = [k for k, v in token_verif_cache.items() if now >= v[1]]
        for k in expired_keys:
            token_verif_cache.pop(k, None)
            
    if token_hash in token_verif_cache:
        email, cache_expiry = token_verif_cache[token_hash]
        if now < cache_expiry:
            return email
            
    try:
        resp = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"access_token": token})
        if resp.status_code != 200:
            print(f"[Auth Error] tokeninfo returned status {resp.status_code}: {resp.text}")
            return None
        data = resp.json()
        
        # Verify audience matches our Client ID (checking aud, issued_to, or audience)
        client_id = data.get("aud") or data.get("issued_to") or data.get("audience")
        if client_id != GOOGLE_CLIENT_ID:
            print(f"[Auth Error] Audience mismatch: got {client_id}, expected {GOOGLE_CLIENT_ID}")
            return None
            
        # Verify scopes include gmail.readonly
        scope = data.get("scope", "")
        if "https://www.googleapis.com/auth/gmail.readonly" not in scope:
            print("[Auth Error] Insufficient scope")
            return None
            
        email = data.get("email")
        if email:
            # Cache verification status for 60 seconds
            token_verif_cache[token_hash] = (email, now + 60.0)
        return email
    except Exception as e:
        print(f"[Auth Error] Failed to contact tokeninfo: {e}")
        return None

def sanitize_filename_suffix(email):
    # Allow alphanumeric characters, dot, dash, underscore, and plus
    if not email or not re.match(r"^[a-zA-Z0-9_\.\-\+]+@[a-zA-Z0-9_\.\-]+\.[a-zA-Z]{2,}$", email):
        raise ValueError("Invalid email format")
    # Replace @, ., and + with underscores to make it filesystem safe
    return email.replace("@", "_").replace(".", "_").replace("+", "_")

def get_user_cache_paths(email):
    suffix = sanitize_filename_suffix(email)
    inbox_path = os.path.join(backend_dir, f"inbox_cache_{suffix}.json")
    digest_path = os.path.join(backend_dir, f"digest_cache_{suffix}.json")
    return inbox_path, digest_path

def get_user_settings_path(email):
    suffix = sanitize_filename_suffix(email)
    return os.path.join(backend_dir, f"user_config_{suffix}.json")

DEFAULT_NEWSLETTERS = [
    "tldrnewsletter.com",
    "morningbrew.com",
    "email.join1440.com",
    "axios.com",
    "theatlantic.com"
]

def load_user_settings(email):
    path = get_user_settings_path(email)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                settings = json.load(f)
                if "subscribed_newsletters" not in settings:
                    settings["subscribed_newsletters"] = DEFAULT_NEWSLETTERS.copy()
                return settings
        except Exception as e:
            print(f"Error loading user settings: {e}")
    return {"subscribed_newsletters": DEFAULT_NEWSLETTERS.copy()}

def save_user_settings(email, settings):
    path = get_user_settings_path(email)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving user settings: {e}")

last_sync_times = {}

def check_sync_rate_limit(email):
    now = time.time()
    
    # Opportunistic cleanup of sync timestamps
    if len(last_sync_times) > 200:
        stale_keys = [k for k, last in last_sync_times.items() if now - last > 60.0]
        for k in stale_keys:
            last_sync_times.pop(k, None)
            
    last_time = last_sync_times.get(email, 0)
    if now - last_time < 15.0:
        return False
    last_sync_times[email] = now
    return True

def get_token_from_request():
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    return None

# Initialize spam filter
spam_filter = SpamFilter()

# Cache paths
inbox_cache_path = os.path.join(backend_dir, "inbox_cache.json")
digest_cache_path = os.path.join(backend_dir, "digest_cache.json")

# Fallback Mock Data matching original mail assistant static mock
from backend.mock_data import DEFAULT_MOCK_INBOX, DEFAULT_MOCK_DIGEST

def run_mock_sync_pipeline(email):
    from backend.mock_data import RAW_MOCK_EMAILS
    raw_emails = RAW_MOCK_EMAILS
    
    spam_emails = []
    newsletter_emails = []
    candidate_emails = []

    # Load user settings/subscribed newsletters
    settings = load_user_settings(email)
    user_subscribed = settings.get("subscribed_newsletters", [])
    subscribed = list(set(user_subscribed + DEFAULT_NEWSLETTERS))

    def is_newsletter_check(email_data, subscribed_list):
        if not subscribed_list:
            return False
        sender_email = email_data.get("from_email", "").strip().lower()
        sender_name = email_data.get("from_name", "").strip().lower()
        domain = sender_email.split("@")[-1].strip(" >") if "@" in sender_email else ""
        for item in subscribed_list:
            item = item.lower().strip()
            if (item == sender_email or 
                item == domain or 
                domain.endswith("." + item) or 
                sender_email.endswith("@" + item) or 
                (len(item) > 2 and item in sender_name)):
                return True
        return False

    for email_data in raw_emails:
        email_data_copy = email_data.copy()
        if is_newsletter_check(email_data_copy, subscribed):
            email_data_copy["isAiFlagged"] = False
            email_data_copy["aiStatus"] = "NEWSLETTER"
            email_data_copy["meta"] = "Inbox / Update"
            newsletter_emails.append(email_data_copy)
        else:
            candidate_emails.append(email_data_copy)

    older_newsletter_emails = []
    if len(newsletter_emails) > 6:
        older_newsletter_emails = newsletter_emails[6:16]
        for email_data in older_newsletter_emails:
            email_data["isAiFlagged"] = False
            email_data["aiStatus"] = "OLDER_NEWSLETTER"
            email_data["meta"] = "Inbox / Older Updates"
        newsletter_emails = newsletter_emails[:6]

    clean_emails = []
    for email_data in candidate_emails:
        subj = email_data["subject"]
        sender = f"{email_data['from_name']} <{email_data['from_email']}>"
        body = email_data["body"]
        if spam_filter.is_spam(subj, sender, body):
            email_data["isAiFlagged"] = False
            email_data["aiStatus"] = "SPAM"
            email_data["meta"] = "Spam / Phishing"
            spam_emails.append(email_data)
        else:
            clean_emails.append(email_data)

    classified_emails = classify_importance_batch(clean_emails)
    digest_data = generate_newsletter_digest(newsletter_emails)

    inbox_data = {}
    all_emails = classified_emails + newsletter_emails + spam_emails + older_newsletter_emails
    for email_data in all_emails:
        msg_id = email_data["id"]
        inbox_data[msg_id] = {
            "from": email_data["from_name"],
            "email": email_data["from_email"],
            "date": email_data["date"],
            "subject": email_data["subject"],
            "meta": email_data["meta"],
            "isAiFlagged": email_data["isAiFlagged"],
            "aiStatus": email_data["aiStatus"],
            "body": email_data["body"],
            "aiReply": "",
            "newsletterBriefing": ""
        }
    
    save_cache(email, inbox_data, digest_data)

mock_sync_lock = threading.Lock()

def load_cached_data(email=None):
    """Loads inbox and digest cached datasets, fallbacks to mock if empty."""
    inbox = DEFAULT_MOCK_INBOX
    digest = DEFAULT_MOCK_DIGEST
    
    inbox_path, digest_path = inbox_cache_path, digest_cache_path
    if email:
        try:
            inbox_path, digest_path = get_user_cache_paths(email)
        except Exception as e:
            print(f"Sanitization error: {e}")
            return inbox, digest
            
    if not os.path.exists(inbox_path):
        if email and "preview" in email:
            with mock_sync_lock:
                if not os.path.exists(inbox_path):
                    print(f"No cache found for preview user {email}. Auto-generating cache via sync pipeline...")
                    try:
                        run_mock_sync_pipeline(email)
                    except Exception as e:
                        print(f"Error running mock sync pipeline: {e}")
                
    if os.path.exists(inbox_path):
        try:
            with open(inbox_path, "r", encoding="utf-8") as f:
                inbox = json.load(f)
        except Exception as e:
            print(f"Error loading inbox cache: {e}")
            
    if os.path.exists(digest_path):
        try:
            with open(digest_path, "r", encoding="utf-8") as f:
                digest = json.load(f)
        except Exception as e:
            print(f"Error loading digest cache: {e}")
            
    return inbox, digest

def save_cache(email, inbox_data, digest_data):
    """Saves inbox and digest datasets to persistent JSON caches."""
    inbox_path, digest_path = inbox_cache_path, digest_cache_path
    if email:
        try:
            inbox_path, digest_path = get_user_cache_paths(email)
        except Exception as e:
            print(f"Sanitization error: {e}")
            return
            
    try:
        with open(inbox_path, "w", encoding="utf-8") as f:
            json.dump(inbox_data, f, indent=2, ensure_ascii=False)
        with open(digest_path, "w", encoding="utf-8") as f:
            json.dump(digest_data, f, indent=2, ensure_ascii=False)
        print(f"Inbox and Digest persistently cached for user {email}.")
    except Exception as e:
        print(f"Error saving persistent caches: {e}")

@app.after_request
def add_cors_headers(response):
    """Enables cross-origin fetches from local file:/// front-ends."""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/api/inbox', methods=['GET'])
def get_inbox():
    token = get_token_from_request()
    email = verify_token_and_get_email(token)
    if not email:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
        
    inbox, _ = load_cached_data(email)
    return jsonify(inbox)

@app.route('/api/digest', methods=['GET'])
def get_digest():
    token = get_token_from_request()
    email = verify_token_and_get_email(token)
    if not email:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
        
    _, digest = load_cached_data(email)
    return jsonify(digest)

@app.route('/api/settings', methods=['GET'])
def get_settings():
    token = get_token_from_request()
    email = verify_token_and_get_email(token)
    if not email:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    settings = load_user_settings(email)
    return jsonify(settings)

@app.route('/api/settings', methods=['POST'])
def save_settings_endpoint():
    token = get_token_from_request()
    email = verify_token_and_get_email(token)
    if not email:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    try:
        data = request.get_json() or {}
        subscribed = data.get("subscribed_newsletters", [])
        if not isinstance(subscribed, list):
            return jsonify({"status": "error", "message": "Invalid settings format"}), 400
        
        # Clean list items
        cleaned = [item.strip() for item in subscribed if isinstance(item, str) and item.strip()]
        
        settings = load_user_settings(email)
        settings["subscribed_newsletters"] = cleaned
        save_user_settings(email, settings)
        
        return jsonify({"status": "success", "message": "Settings updated successfully."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/sync', methods=['POST'])
def sync_emails():
    token = get_token_from_request()
    email = verify_token_and_get_email(token)
    if not email:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
        
    # Enforce sync rate limit (1 sync per 15s per email)
    if not check_sync_rate_limit(email):
        return jsonify({
            "status": "error",
            "message": "Sync rate limit reached. Please wait a moment."
        }), 429
        
    try:
        # Load Gmail Fetch Layer using dynamic token
        print(f"Starting inbox sync for user: {email}...")
        if token and token.startswith("mock_token_"):
            from backend.mock_data import RAW_MOCK_EMAILS
            raw_emails = RAW_MOCK_EMAILS
        else:
            raw_emails = fetch_recent_emails(token, limit=75)
        if not raw_emails:
            return jsonify({
                "status": "error",
                "message": "Failed to fetch emails or inbox is empty."
            }), 400

        spam_emails = []
        newsletter_emails = []
        candidate_emails = []  # Emails that will go through the spam + importance pipeline

        # Load user settings/subscribed newsletters
        settings = load_user_settings(email)
        user_subscribed = settings.get("subscribed_newsletters", [])
        # Always merge DEFAULT_NEWSLETTERS to make sure they are always whitelisted
        subscribed = list(set(user_subscribed + DEFAULT_NEWSLETTERS))

        # ── Step 0: Newsletter Pre-filter (runs BEFORE spam ML) ──────────────
        print(f"Pre-filtering newsletters (subscribed list: {subscribed})...")
        from backend.classify_importance import is_newsletter_heuristic
        
        def is_newsletter_check(email_data, subscribed_list):
            if not subscribed_list:
                return False
            
            sender_email = email_data.get("from_email", "").strip().lower()
            sender_name = email_data.get("from_name", "").strip().lower()
            domain = sender_email.split("@")[-1].strip(" >") if "@" in sender_email else ""
            
            for item in subscribed_list:
                item = item.lower().strip()
                # Check match
                if (item == sender_email or 
                    item == domain or 
                    domain.endswith("." + item) or 
                    sender_email.endswith("@" + item) or 
                    (len(item) > 2 and item in sender_name)):
                    print(f"[Newsletter Match] '{sender_email}' matched whitelisted item '{item}'")
                    return True
            return False

        for email_data in raw_emails:
            if is_newsletter_check(email_data, subscribed):
                email_data["isAiFlagged"] = False
                email_data["aiStatus"] = "NEWSLETTER"
                email_data["meta"] = "Inbox / Update"
                newsletter_emails.append(email_data)
            else:
                candidate_emails.append(email_data)

        # Enforce hard limit of at most 6 newsletters (newest first)
        older_newsletter_emails = []
        if len(newsletter_emails) > 6:
            older_newsletter_emails = newsletter_emails[6:16]  # additional 10 emails at max
            for email_data in older_newsletter_emails:
                email_data["isAiFlagged"] = False
                email_data["aiStatus"] = "OLDER_NEWSLETTER"
                email_data["meta"] = "Inbox / Older Updates"
            print(f"Limiting newsletters: kept 6 active newsletters, routed {len(older_newsletter_emails)} to older section.")
            newsletter_emails = newsletter_emails[:6]

        # ── Step 1: Spam Filter (only runs on non-newsletter emails) ─────────
        print(f"Filtering spam emails from {len(candidate_emails)} candidate emails...")
        clean_emails = []
        for email_data in candidate_emails:
            subj = email_data["subject"]
            sender = f"{email_data['from_name']} <{email_data['from_email']}>"
            body = email_data["body"]

            if spam_filter.is_spam(subj, sender, body):
                email_data["isAiFlagged"] = False
                email_data["aiStatus"] = "SPAM"
                email_data["meta"] = "Spam / Phishing"
                spam_emails.append(email_data)
            else:
                clean_emails.append(email_data)

        # ── Step 2: Importance Classification (heuristics + ML + LLM) ───────
        print(f"Running importance classifier on {len(clean_emails)} clean emails...")
        classified_emails = classify_importance_batch(clean_emails)

        # ── Step 3: Generate Newsletter Digests ──────────────────────────────
        print(f"Compiling newsletter digests from {len(newsletter_emails)} newsletters...")
        digest_data = generate_newsletter_digest(newsletter_emails)

        # ── Step 4: Format to contract schema ────────────────────────────────
        inbox_data = {}
        all_emails = classified_emails + newsletter_emails + spam_emails + older_newsletter_emails

        # Load previous cache if exists to preserve manual briefing fields
        prev_inbox, _ = load_cached_data(email)

        for email_data in all_emails:
            msg_id = email_data["id"]
            # Look up if this email has a briefing in previous cache
            prev_item = prev_inbox.get(str(msg_id))
            prev_briefing = prev_item.get("newsletterBriefing", "") if prev_item else ""
            
            inbox_data[msg_id] = {
                "from": email_data["from_name"],
                "email": email_data["from_email"],
                "date": email_data["date"],
                "subject": email_data["subject"],
                "meta": email_data["meta"],
                "isAiFlagged": email_data["isAiFlagged"],
                "aiStatus": email_data["aiStatus"],
                "body": email_data["body"],
                "aiReply": "",  # Handled on-demand via /api/draft-reply
                "newsletterBriefing": prev_briefing  # Preserve existing briefing if present
            }

        # Write to user-specific cache
        save_cache(email, inbox_data, digest_data)

        return jsonify({
            "status": "success",
            "message": "Inbox synced successfully.",
            "synced_count": len(all_emails),
            "breakdown": {
                "newsletters": len(newsletter_emails),
                "spam": len(spam_emails),
                "classified": len(classified_emails),
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Sync pipeline failed: {str(e)}"
        }), 500

@app.route('/api/draft-reply', methods=['POST'])
def draft_reply():
    """Generates an LLM response draft for a specific email on-demand (Phase 8)."""
    token = get_token_from_request()
    email = verify_token_and_get_email(token)
    if not email:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
        
    try:
        req_data = request.get_json() or {}
        email_id = req_data.get("id")
        if not email_id:
            return jsonify({"status": "error", "message": "Missing email 'id' parameter."}), 400
            
        # Load user-specific inbox cache
        inbox, digest = load_cached_data(email)
        email_item = inbox.get(str(email_id))
        
        if not email_item:
            return jsonify({"status": "error", "message": "Email not found."}), 404
            
        print(f"[LLM Draft] Creating draft response for: {email_item['subject']} from {email_item['from']}")
        
        # Call LLM to generate response draft (personalized with the user's name)
        first_name = email.split("@")[0].split("+")[0].split(".")[0].split("_")[0].capitalize()
        system_instruction = (
            f"You are {first_name}'s helpful email writing assistant. "
            f"Write a brief, professional, and friendly email reply on behalf of {first_name}. "
            f"Address the sender by name. Keep the reply short (3 to 4 sentences maximum) "
            f"and sign off as '{first_name}'. Do not add subject lines or placeholders."
        )
        
        prompt = (
            f"Please draft a reply to the following email:\n\n"
            f"From: {email_item['from']} <{email_item['email']}>\n"
            f"Subject: {email_item['subject']}\n"
            f"Body:\n{email_item['body']}"
        )
        
        draft_text = call_llm(prompt, system_instruction=system_instruction, json_mode=False)
        
        # Save draft back into cache so it persists if the user switches emails
        inbox[str(email_id)]["aiReply"] = draft_text
        save_cache(email, inbox, digest)
        
        return jsonify({
            "status": "success",
            "draft": draft_text
        })
        
    except Exception as e:
        print(f"Error drafting reply: {e}")
        return jsonify({
            "status": "error",
            "message": f"Failed to draft reply: {str(e)}"
        }), 500
@app.route('/api/brief-newsletter', methods=['POST'])
def brief_newsletter():
    token = get_token_from_request()
    email = verify_token_and_get_email(token)
    if not email:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
        
    try:
        req_data = request.get_json() or {}
        email_id = req_data.get("id")
        if not email_id:
            return jsonify({"status": "error", "message": "Missing email 'id' parameter."}), 400
            
        inbox, digest = load_cached_data(email)
        email_item = inbox.get(str(email_id))
        
        if not email_item:
            return jsonify({"status": "error", "message": "Email not found."}), 404
            
        print(f"[LLM Newsletter Briefing] Creating briefing for: {email_item['subject']}")
        
        system_instruction = (
            "You are a smart email summary assistant. "
            "Write a very concise summary (maximum 2 to 3 sentences) of this newsletter email. "
            "Focus on the main highlights, key updates, or actionable insights. "
            "Keep the tone professional and clean. Do not add headers, list bullets, or markdown formatting."
        )
        
        prompt = (
            f"Please summarize this newsletter:\n\n"
            f"From: {email_item['from']} <{email_item['email']}>\n"
            f"Subject: {email_item['subject']}\n"
            f"Body:\n{email_item['body']}"
        )
        
        brief_text = call_llm(prompt, system_instruction=system_instruction, json_mode=False)
        
        # Save briefing back into cache
        inbox[str(email_id)]["newsletterBriefing"] = brief_text
        save_cache(email, inbox, digest)
        
        return jsonify({
            "status": "success",
            "briefing": brief_text
        })
    except Exception as e:
        print(f"Error briefing newsletter: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Mail Assist backend server on http://localhost:{port}...")
    print(f"Active Google Client ID configured on backend: {GOOGLE_CLIENT_ID}")
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
