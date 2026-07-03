import os
import base64
from email.utils import parseaddr
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """
    Authenticates and builds the Gmail API service.
    Token loading priority:
      1. GMAIL_TOKEN_JSON env var (Heroku / production)
      2. backend/token.json file  (local development)
    """
    import json as _json

    creds = None
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(backend_dir, 'token.json')
    credentials_path = os.path.join(backend_dir, '..', 'credentials.json')

    # ── Priority 1: env var (Heroku) ─────────────────────────────────────
    token_json_str = os.environ.get("GMAIL_TOKEN_JSON", "")
    if token_json_str:
        try:
            token_data = _json.loads(token_json_str)
            creds = Credentials.from_authorized_user_info(token_data, SCOPES)
        except Exception as e:
            print(f"[Gmail Auth] Failed to load token from GMAIL_TOKEN_JSON env var: {e}")
            creds = None

    # ── Priority 2: local token.json file ────────────────────────────────
    if not creds and os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # ── Refresh if expired ───────────────────────────────────────────────
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Write refreshed token back to file (local) if available
                if os.path.exists(token_path):
                    with open(token_path, 'w') as token:
                        token.write(creds.to_json())
            except Exception as e:
                print(f"[Gmail Auth] Error refreshing access token: {e}")
                creds = None

        # ── Local-only: interactive browser OAuth flow ───────────────────
        # This path cannot run on Heroku (no browser). Run locally first,
        # then upload the generated token.json as GMAIL_TOKEN_JSON config var.
        if not creds:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    "Google API credentials file not found. "
                    "Set GMAIL_TOKEN_JSON env var on Heroku, or place credentials.json locally."
                )
            if token_json_str:
                # We are on a server — cannot open a browser
                raise RuntimeError(
                    "Gmail token is invalid or expired and cannot be refreshed. "
                    "Re-run auth locally and update the GMAIL_TOKEN_JSON config var on Heroku."
                )
            print("Opening browser for Gmail OAuth...")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(host='127.0.0.1', port=8080)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

def decode_body_data(data):
    """Safely decodes base64url data."""
    try:
        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error decoding body data: {e}")
        return ""

def extract_body(payload):
    """Extracts raw body text from message payload, preferring text/plain, then converting text/html."""
    if 'parts' in payload:
        return extract_parts_body(payload['parts'])
    
    body_data = payload.get('body', {}).get('data', '')
    if body_data:
        mime_type = payload.get('mimeType', 'text/plain')
        decoded = decode_body_data(body_data)
        if mime_type == 'text/html':
            soup = BeautifulSoup(decoded, 'html.parser')
            return soup.get_text(separator='\n')
        return decoded
    return ""

def extract_parts_body(parts):
    """Recursively processes multipart message parts."""
    text_parts = []
    html_parts = []
    
    for part in parts:
        mime_type = part.get('mimeType')
        body_data = part.get('body', {}).get('data', '')
        
        if mime_type == 'text/plain' and body_data:
            text_parts.append(decode_body_data(body_data))
        elif mime_type == 'text/html' and body_data:
            html_parts.append(decode_body_data(body_data))
        elif 'parts' in part:
            nested_body = extract_parts_body(part['parts'])
            if nested_body:
                text_parts.append(nested_body)
                
    if text_parts:
        return "\n".join(text_parts)
    elif html_parts:
        # Fallback to HTML conversion if text is empty
        full_html = "\n".join(html_parts)
        soup = BeautifulSoup(full_html, 'html.parser')
        return soup.get_text(separator='\n')
    return ""

def fetch_recent_emails(limit=30):
    """Fetches list of recent emails from Gmail, returning clean intermediate data."""
    try:
        service = get_gmail_service()
    except FileNotFoundError as e:
        print(e)
        return []
    except Exception as e:
        print(f"Authentication/Setup error with Gmail service: {e}")
        return []

    print(f"Fetching recent {limit} messages...")
    try:
        # We query for general messages. User can refine this search.
        results = service.users().messages().list(userId='me', maxResults=limit).execute()
        messages = results.get('messages', [])
        
        email_list = []
        for msg in messages:
            msg_id = msg['id']
            # Fetch full message payload
            msg_detail = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            
            payload = msg_detail.get('payload', {})
            headers = payload.get('headers', [])
            
            # Parse key headers
            from_header = ""
            subject_header = "(No Subject)"
            date_header = ""
            list_unsubscribe = ""
            
            for h in headers:
                name = h.get('name', '').lower()
                val = h.get('value', '')
                if name == 'from':
                    from_header = val
                elif name == 'subject':
                    subject_header = val
                elif name == 'date':
                    date_header = val
                elif name == 'list-unsubscribe':
                    list_unsubscribe = val
            
            # Extract name and email address from header
            sender_name, sender_email = parseaddr(from_header)
            if not sender_name:
                sender_name = sender_email.split('@')[0] if '@' in sender_email else sender_email
                
            snippet = msg_detail.get('snippet', '')
            body = extract_body(payload)
            if not body:
                body = snippet
                
            email_list.append({
                "id": msg_id,
                "from_name": sender_name,
                "from_email": sender_email,
                "subject": subject_header,
                "date": date_header,
                "snippet": snippet,
                "body": body,
                "list_unsubscribe": list_unsubscribe
            })
            
        print(f"Successfully fetched and parsed {len(email_list)} messages.")
        return email_list
    except Exception as e:
        print(f"Error fetching emails from Gmail API: {e}")
        return []
