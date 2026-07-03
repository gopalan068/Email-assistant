import os
import sys
import json
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

app = Flask(__name__)

# Initialize spam filter
spam_filter = SpamFilter()

# Cache paths
inbox_cache_path = os.path.join(backend_dir, "inbox_cache.json")
digest_cache_path = os.path.join(backend_dir, "digest_cache.json")

# Fallback Mock Data matching original mail assistant static mock
mock_data_path = os.path.join(backend_dir, "mock_data.py")
class DummyFile:
    def write(self, text): pass
    def __enter__(self): return self
    def __exit__(self, *args): pass

f = open(mock_data_path, "w", encoding="utf-8") if not os.path.exists(mock_data_path) else DummyFile()
with f:
    f.write('''# Default fallback mock data
DEFAULT_MOCK_INBOX = {
  "1": {
    "from": "Bank of India",
    "email": "notifications@bankofindia.co.in",
    "date": "August 2, 2026",
    "subject": "Loan repayment reminder",
    "meta": "Inbox / Finance",
    "isAiFlagged": True,
    "aiStatus": "IMPORTANT",
    "body": "Dear Customer,\\n\\nThis is a friendly reminder that your monthly Home Loan EMI payment of \\u20b924,500 (Account ending in *8824) is scheduled for auto-debit on August 5, 2026.\\n\\nPlease ensure your account maintains a sufficient balance prior to the debit date to avoid any late payment fees, bounce penalties, or credit score adjustments.\\n\\nIf you have already made the transfer, please disregard this automated notification.\\n\\nWarm regards,\\nRetail Lending Operations\\nBank of India",
    "aiReply": "Log confirmation: Checked balance (current: \\u20b942,100). Auto-repayment scheduled. Remind me again on Aug 4."
  },
  "2": {
    "from": "Meera (Manager)",
    "email": "meera.sharma@corp.com",
    "date": "August 2, 2026 (10:15 AM)",
    "subject": "Urgent: Q3 review slides",
    "meta": "Inbox / Work",
    "isAiFlagged": False,
    "aiStatus": "DIRECT CORRESPONDENCE",
    "body": "Hi Gopal,\\n\\nHope you are having a productive week.\\n\\nThe leadership team has moved the Q3 Business Review meeting up to Thursday morning. Because of this schedule shift, I need to compile all team slides by this evening.\\n\\nCould you please share your draft Q3 slides by EOD today? Let me know if you need any assistance compiling the customer satisfaction charts.\\n\\nThanks,\\nMeera",
    "aiReply": "Hi Meera,\\n\\nI am finalizing the Q3 slide deck and customer satisfaction charts now. I will have it uploaded and shared with you by 5:00 PM today. Let me know if you want to do a quick sync before the review.\\n\\nBest,\\nGopal"
  },
  "3": {
    "from": "Freelance Client",
    "email": "billing@indiedesigns.studio",
    "date": "August 1, 2026",
    "subject": "Invoice #INV-204 payment sent",
    "meta": "Inbox / Payment",
    "isAiFlagged": False,
    "aiStatus": "PAYMENT INBOUND",
    "body": "Hi Gopal,\\n\\nJust a quick update that I've processed the payment for Invoice #INV-204 ($1,200) for the landing page project today.\\n\\nIt has been sent via bank wire, so it should reflect in your account within the next 2-3 business days depending on interbank processing speeds.\\n\\nLet me know once you see it on your end. It was absolute pleasure working with you on this launch!\\n\\nBest regards,\\nSarah K.",
    "aiReply": "Hi Sarah,\\n\\nThank you for processing the payment for invoice #INV-204. I will monitor my account and confirm as soon as the funds clear. It was a pleasure working with you on the landing page project as well!\\n\\nBest regards,\\nGopal"
  },
  "4": {
    "from": "Dentist Clinic",
    "email": "reception@pearlywhites.com",
    "date": "August 1, 2026",
    "subject": "Appointment tomorrow at 11 AM",
    "meta": "Inbox / Health",
    "isAiFlagged": False,
    "aiStatus": "SCHEDULED EVENT",
    "body": "Dear Gopal,\\n\\nThis is a friendly reminder of your upcoming dental appointment tomorrow, August 3, at 11:00 AM at Pearly Whites Dental Clinic.\\n\\nYour session is scheduled for a routine cleaning and general checkup with Dr. Roy. Please try to arrive about 10 minutes early to check-in at reception.\\n\\nIf you need to reschedule or cancel, please call us at least 12 hours in advance.\\n\\nSincerely,\\nPearly Whites Dental Team",
    "aiReply": "Hi Pearly Whites Team,\\n\\nThank you for the reminder. I confirm that I will be arriving tomorrow at 11:00 AM for my checkup with Dr. Roy.\\n\\nBest,\\nGopal"
  },
  "5": {
    "from": "winbig@lottery.xyz",
    "email": "claims-department@winbiglottery.xyz",
    "date": "July 30, 2026",
    "subject": "\\ud83c\\udf89 You won $5,000,000!",
    "meta": "Spam / Phishing",
    "isAiFlagged": True,
    "aiStatus": "AUTO-BLOCKED / PHISHING",
    "body": "DEAR LUCKY WINNER,\\n\\nYOUR EMAIL ADDRESS HAS WON THE GRAND PRIZE OF FIVE MILLION DOLLARS ($5,000,000.00) IN THE GLOBAL EMAIL LOTTERY SWEEPSTAKES RUN BY THE TRUSTEES.\\n\\nTO CLAIM YOUR PRIZE IMMEDIATELY, PLEASE CLICK ON THE SECURE LINK BELOW AND FILL OUT YOUR BANK ROUTING DETAILS AND SCAN OF PASSPORT:\\n\\nhttp://suspicious-link-to-steal-your-identity.xyz/claim-prize\\n\\nDO NOT SHARE THIS EMAIL WITH ANYONE TO PREVENT DOUBLE CLAIMS.\\n\\nYours faithfully,\\nLottery Claims Committee",
    "aiReply": "Action Logged: No response recommended. This is a phishing scam. Auto-reported to security and blacklisted."
  },
  "6": {
    "from": "cheapmeds@discount.net",
    "email": "deals@cheapmeds-discount.net",
    "date": "July 29, 2026",
    "subject": "70% OFF all medicines \\ud83d\\udc8a",
    "meta": "Spam / Commercial",
    "isAiFlagged": True,
    "aiStatus": "AUTO-BLOCKED / SCAM",
    "body": "HELLO FRIEND!\\n\\nSAVE BIG TODAY ON ALL YOUR ESSENTIAL MEDICINES. WE OFFER 70% DISCOUNT ON ALL POPULAR PHARMACEUTICAL BRANDS!\\n\\n- NO PRESCRIPTIONS REQUIRED\\n- 100% DISCREET PACKAGING AND SECURE DELIVERY\\n- FREE SHIPPING ON ALL ORDERS OVER $50\\n\\nORDER NOW TO BEAT THE PRICE HIKE: http://scam-pharmacy.net",
    "aiReply": "Action Logged: Sender auto-blocked. Email quarantined."
  },
  "7": {
    "from": "Zomato",
    "email": "offers@zomato-mail.com",
    "date": "Today (11:40 AM)",
    "subject": "Your last order: 20% off next meal",
    "meta": "Inbox / Promo",
    "isAiFlagged": False,
    "aiStatus": "PROMOTIONAL",
    "body": "Hey Gopal,\\n\\nHow did you like your meal from Punjab Grill? We hope it was absolutely delicious!\\n\\nAs a thank you for ordering with us, here's an exclusive 20% discount coupon for your next meal (up to \\u20b9100). Use code CRITIC20 at checkout.\\n\\nValid for the next 3 days on orders above \\u20b9199.\\n\\nEnjoy your meal!",
    "aiReply": "Action: Archive. Coupon Code logged: CRITIC20 (expires in 3 days)."
  },
  "8": {
    "from": "LinkedIn",
    "email": "connections@linkedin.com",
    "date": "Today (9:00 AM)",
    "subject": "5 new connection requests",
    "meta": "Inbox / Social",
    "isAiFlagged": False,
    "aiStatus": "SOCIAL ALERTS",
    "body": "Hi Gopal,\\n\\nYou have 5 new pending connection requests waiting for your response on LinkedIn:\\n\\n- Ankit Verma (Software Engineer at TechCorp)\\n- Priya Patel (UI/UX Designer)\\n- ... and 3 other professionals in your network.\\n\\nGrow your network and see what they are posting today.\\n\\nSincerely,\\nThe LinkedIn Team",
    "aiReply": "Action: Queue for manual review. Open LinkedIn to approve connection requests."
  },
  "9": {
    "from": "Amazon",
    "email": "shipment-tracking@amazon.in",
    "date": "Yesterday",
    "subject": "Your order has shipped",
    "meta": "Inbox / Shipping",
    "isAiFlagged": False,
    "aiStatus": "TRANSACTIONAL",
    "body": "Dear Gopal,\\n\\nYour order containing the \\"AmazonBasics USB-C to USB-A Cable (3 ft)\\" has been shipped and is currently in transit.\\n\\nYour package is expected to arrive on Friday, August 7 by 8:00 PM.\\n\\nTracking ID: AZ8821948B\\nCarrier: Amazon Logistics\\n\\nYou can track your package details inside your account at any time.",
    "aiReply": "Action: Auto-tracked. Delivery expected Friday, August 7. Track ID: AZ8821948B."
  },
  "10": {
    "from": "Gym",
    "email": "info@corefitnessgym.com",
    "date": "July 31, 2026",
    "subject": "New yoga classes starting Monday",
    "meta": "Inbox / Update",
    "isAiFlagged": False,
    "aiStatus": "NEWSLETTER",
    "body": "Hi Fitness Enthusiasts,\\n\\nWe are active to announce new morning Yoga and Mindfulness classes starting this Monday at Core Fitness gym!\\n\\nClass schedule:\\n- Monday & Wednesday: 6:30 AM - 7:30 AM\\n- Friday: 7:00 AM - 8:00 AM\\n\\nSign up by this weekend to claim a 15% early-bird discount on monthly packages. Spaces are limited!\\n\\nGet active,\\nCore Fitness Gym",
    "aiReply": "Hi Core Fitness Gym,\\n\\nThanks for the update. Could you please send me details about the monthly pricing for the yoga batch? Thanks,\\nGopal"
  }
}

DEFAULT_MOCK_DIGEST = [
  {
    "source": "Morning Brew",
    "time": "[~40 sec read]",
    "points": [
      "Markets dip as Fed holds interest rates steady",
      "Apple Vision Pro sales exceed expectations in early quarters",
      "Quick take: SEC releases new crypto regulation framework updates"
    ]
  },
  {
    "source": "TLDR Newsletter",
    "time": "[~35 sec read]",
    "points": [
      "OpenAI releases new reasoning model focusing on math and science",
      "Meta's open-source Llama model beats leading commercial benchmarks",
      "Startup funding roundup: AI infrastructure remains dominant"
    ]
  },
  {
    "source": "Frontend Focus",
    "time": "[~30 sec read]",
    "points": [
      "React Server Components now stable in major meta-frameworks",
      "A comprehensive guide to CSS Container Queries and queryable state",
      "New JavaScript runtime Bun v1.2 introduces performance boosts"
    ]
  }
]
''')

# Import mocks from the file we just created
from backend.mock_data import DEFAULT_MOCK_INBOX, DEFAULT_MOCK_DIGEST

def load_cached_data():
    """Loads inbox and digest cached datasets, fallbacks to mock if empty."""
    inbox = DEFAULT_MOCK_INBOX
    digest = DEFAULT_MOCK_DIGEST
    
    if os.path.exists(inbox_cache_path):
        try:
            with open(inbox_cache_path, "r", encoding="utf-8") as f:
                inbox = json.load(f)
        except Exception as e:
            print(f"Error loading inbox cache: {e}")
            
    if os.path.exists(digest_cache_path):
        try:
            with open(digest_cache_path, "r", encoding="utf-8") as f:
                digest = json.load(f)
        except Exception as e:
            print(f"Error loading digest cache: {e}")
            
    return inbox, digest

def save_cache(inbox_data, digest_data):
    """Saves inbox and digest datasets to persistent JSON caches."""
    try:
        with open(inbox_cache_path, "w", encoding="utf-8") as f:
            json.dump(inbox_data, f, indent=2, ensure_ascii=False)
        with open(digest_cache_path, "w", encoding="utf-8") as f:
            json.dump(digest_data, f, indent=2, ensure_ascii=False)
        print("Inbox and Digest persistently cached.")
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
    inbox, _ = load_cached_data()
    return jsonify(inbox)

@app.route('/api/digest', methods=['GET'])
def get_digest():
    _, digest = load_cached_data()
    return jsonify(digest)

@app.route('/api/sync', methods=['POST'])
def sync_emails():
    try:
        # Load Gmail Fetch Layer
        print("Starting inbox sync...")
        raw_emails = fetch_recent_emails(limit=30)
        if not raw_emails:
            return jsonify({
                "status": "error",
                "message": "Gmail OAuth token missing or failed to fetch. Please verify setup."
            }), 400

        spam_emails = []
        newsletter_emails = []
        candidate_emails = []  # Emails that will go through the spam + importance pipeline

        # ── Step 0: Newsletter Pre-filter (runs BEFORE spam ML) ──────────────
        # Newsletters must be separated first because the Enron-trained spam model
        # will mis-classify promotional/newsletter emails as spam (they share vocabulary).
        print("Pre-filtering newsletters...")
        from backend.classify_importance import is_newsletter_heuristic
        for email in raw_emails:
            if is_newsletter_heuristic(email):
                email["isAiFlagged"] = False
                email["aiStatus"] = "NEWSLETTER"
                email["meta"] = "Inbox / Update"
                newsletter_emails.append(email)
            else:
                candidate_emails.append(email)

        # ── Step 1: Spam Filter (only runs on non-newsletter emails) ─────────
        print(f"Filtering spam emails from {len(candidate_emails)} candidate emails...")
        clean_emails = []
        for email in candidate_emails:
            subj = email["subject"]
            sender = f"{email['from_name']} <{email['from_email']}>"
            body = email["body"]

            if spam_filter.is_spam(subj, sender, body):
                email["isAiFlagged"] = False
                email["aiStatus"] = "SPAM"
                email["meta"] = "Spam / Phishing"
                spam_emails.append(email)
            else:
                clean_emails.append(email)

        # ── Step 2: Importance Classification (heuristics + ML + LLM) ───────
        print(f"Running importance classifier on {len(clean_emails)} clean emails...")
        classified_emails = classify_importance_batch(clean_emails)

        # ── Step 3: Generate Newsletter Digests ──────────────────────────────
        print(f"Compiling newsletter digests from {len(newsletter_emails)} newsletters...")
        digest_data = generate_newsletter_digest(newsletter_emails)

        # ── Step 4: Format to contract schema ────────────────────────────────
        inbox_data = {}
        all_emails = classified_emails + newsletter_emails + spam_emails

        for email in all_emails:
            msg_id = email["id"]
            inbox_data[msg_id] = {
                "from": email["from_name"],
                "email": email["from_email"],
                "date": email["date"],
                "subject": email["subject"],
                "meta": email["meta"],
                "isAiFlagged": email["isAiFlagged"],
                "aiStatus": email["aiStatus"],
                "body": email["body"],
                "aiReply": ""  # Handled on-demand via /api/draft-reply
            }

        # Write to cache
        save_cache(inbox_data, digest_data)

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
    try:
        req_data = request.get_json() or {}
        email_id = req_data.get("id")
        if not email_id:
            return jsonify({"status": "error", "message": "Missing email 'id' parameter."}), 400
            
        # Load inbox cache to read email details
        inbox, _ = load_cached_data()
        email = inbox.get(str(email_id))
        
        if not email:
            return jsonify({"status": "error", "message": "Email not found."}), 404
            
        print(f"[LLM Draft] Creating draft response for: {email['subject']} from {email['from']}")
        
        # Call LLM to generate response draft
        system_instruction = (
            "You are Gopal's helpful email writing assistant. "
            "Write a brief, professional, and friendly email reply on behalf of Gopal. "
            "Address the sender by name. Keep the reply short (3 to 4 sentences maximum) "
            "and sign off as 'Gopal'. Do not add subject lines or placeholders."
        )
        
        prompt = (
            f"Please draft a reply to the following email:\n\n"
            f"From: {email['from']} <{email['email']}>\n"
            f"Subject: {email['subject']}\n"
            f"Body:\n{email['body']}"
        )
        
        draft_text = call_llm(prompt, system_instruction=system_instruction, json_mode=False)
        
        # Save draft back into cache so it persists if the user switches emails
        inbox[email_id]["aiReply"] = draft_text
        save_cache(inbox, _)
        
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Mail Assist backend server on http://localhost:{port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
