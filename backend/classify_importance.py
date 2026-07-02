import json
import re
from .llm_client import call_llm

def is_newsletter_heuristic(email_data) -> bool:
    """
    Applies heuristics to check if the email is a newsletter/automated update.
    """
    sender_email = email_data.get("from_email", "").lower()
    sender_name = email_data.get("from_name", "").lower()
    body = email_data.get("body", "").lower()
    list_unsubscribe = email_data.get("list_unsubscribe", "")

    # Rule 1: List-Unsubscribe header present
    if list_unsubscribe and len(list_unsubscribe.strip()) > 0:
        return True

    # Rule 2: Sender email contains newsletter/notification indicator
    indicators = ["no-reply", "noreply", "newsletter", "notification", "digest", "update", "news", "info@"]
    if any(ind in sender_email for ind in indicators):
        return True

    # Rule 3: Sender name contains notification indicator
    name_indicators = ["newsletter", "notification", "digest", "updates", "support"]
    if any(ind in sender_name for ind in name_indicators):
        return True

    # Rule 4: Body contains unsubscribe links/words
    if "unsubscribe" in body or "view in browser" in body or "opt out" in body:
        return True

    return False

def classify_importance_batch(emails):
    """
    Classifies a list of emails into 'important' or 'regular' using a single batched LLM call.
    Modifies emails in-place, adding 'isAiFlagged', 'aiStatus', and 'meta'.
    """
    regular_emails = []
    
    # 1. First pass: Apply heuristic filters
    for email in emails:
        if is_newsletter_heuristic(email):
            email["isAiFlagged"] = False
            email["aiStatus"] = "NEWSLETTER"
            email["meta"] = "Inbox / Update"
        else:
            regular_emails.append(email)
            
    if not regular_emails:
        return emails

    # 2. Batch classification for remaining regular emails
    # Prepare batch data payload
    batch_input = []
    for email in regular_emails:
        batch_input.append({
            "id": email["id"],
            "sender": f"{email['from_name']} <{email['from_email']}>",
            "subject": email["subject"],
            "snippet": email["snippet"][:200]  # truncate snippet to keep token usage low
        })

    system_instruction = (
        "You are an expert email triage assistant. Your task is to analyze a batch of emails and classify each as 'important' or 'regular'.\n\n"
        "An email is 'important' if:\n"
        "- It requires immediate response, attention, or action from the user.\n"
        "- It is a direct correspondence or request from a colleague, manager, client, partner, or family member.\n"
        "- It contains critical financial alerts, bill payment reminders, or transaction receipts.\n"
        "- It contains health check reminders or booking confirmations.\n\n"
        "An email is 'regular' if:\n"
        "- It is a promotional offer, social alert, routine status report, or general automated notification.\n"
        "- It does not require urgent response or immediate action.\n\n"
        "You must return a JSON object where each key is the email ID and the value is an object containing 'importance' ('important' or 'regular') and a one-sentence 'reason'.\n"
        "Example output:\n"
        "{\n"
        "  \"msg_101\": {\"importance\": \"important\", \"reason\": \"Urgent request from manager to review Q3 presentation slides by EOD.\"},\n"
        "  \"msg_102\": {\"importance\": \"regular\", \"reason\": \"Automated social media alert about new connection requests.\"}\n"
        "}"
    )

    prompt = (
        "Please classify the following batch of emails and return the results as a JSON object matching the requested schema.\n\n"
        f"Emails:\n{json.dumps(batch_input, indent=2)}"
    )

    try:
        response_text = call_llm(prompt, system_instruction=system_instruction, json_mode=True)
        # Parse output
        results = json.loads(response_text)
        
        # Log token metrics approximately
        input_tokens = len(system_instruction.split()) + len(prompt.split())
        output_tokens = len(response_text.split())
        print(f"[LLM Classify] Processed {len(batch_input)} emails. Approx input tokens: {input_tokens}, output tokens: {output_tokens}")
        
        # Apply classifications back to original emails
        for email in regular_emails:
            msg_id = email["id"]
            classification = results.get(msg_id, {})
            importance = classification.get("importance", "regular").lower()
            reason = classification.get("reason", "")
            
            if importance == "important":
                email["isAiFlagged"] = True
                email["aiStatus"] = "IMPORTANT"
                # Extract simple category from reason if possible, or default
                email["meta"] = determine_meta_category(email, reason, True)
            else:
                email["isAiFlagged"] = False
                email["aiStatus"] = "REGULAR"
                email["meta"] = determine_meta_category(email, reason, False)
                
    except Exception as e:
        print(f"Error during batched importance classification: {e}. Falling back to regular classification.")
        for email in regular_emails:
            email["isAiFlagged"] = False
            email["aiStatus"] = "REGULAR"
            email["meta"] = "Inbox / Regular"
            
    return emails

def determine_meta_category(email, reason, is_important) -> str:
    """Helper to guess a tag category like Work, Finance, Social, etc."""
    subject = email.get("subject", "").lower()
    body = email.get("body", "").lower()
    
    # Financial keywords
    fin_keywords = ["invoice", "payment", "bank", "credit", "debit", "repayment", "emi", "transaction", "billing", "receipt"]
    if any(k in subject or k in body for k in fin_keywords):
        return "Inbox / Finance"
        
    # Work keywords
    work_keywords = ["review", "slides", "deck", "meeting", "sync", "project", "client", "schedule", "deadline", "urgency", "tasks"]
    if any(k in subject or k in body for k in work_keywords):
        return "Inbox / Work"
        
    # Health keywords
    health_keywords = ["appointment", "dentist", "doctor", "clinic", "checkup", "medical"]
    if any(k in subject or k in body for k in health_keywords):
        return "Inbox / Health"

    # Social keywords
    social_keywords = ["linkedin", "facebook", "twitter", "connection", "message from"]
    if any(k in subject or k in body for k in social_keywords):
        return "Inbox / Social"
        
    return "Inbox / Important" if is_important else "Inbox / Regular"
