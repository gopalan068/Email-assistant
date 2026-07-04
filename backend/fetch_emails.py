import os
import base64
import json
from email.utils import parseaddr
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Helper to authenticate and build the Gmail API service."""
    creds = None
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(backend_dir, 'token.json')
    credentials_path = os.path.join(backend_dir, '..', 'credentials.json')
    
    # 1. Try loading from GMAIL_TOKEN_JSON environment variable (Render/Cloud support)
    env_token = os.environ.get("GMAIL_TOKEN_JSON")
    if env_token:
        try:
            creds_info = json.loads(env_token)
            creds = Credentials.from_authorized_user_info(creds_info, SCOPES)
            print("Loaded Gmail credentials from GMAIL_TOKEN_JSON environment variable.")
        except Exception as e:
            print(f"Error loading credentials from GMAIL_TOKEN_JSON: {e}")
            creds = None

    # 2. Fallback to local token.json file
    if not creds and os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        print("Loaded Gmail credentials from token.json file.")
        
    # If there are no (valid) credentials available, refresh or authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("Successfully refreshed Gmail access token.")
                # Save refreshed credentials locally if writable (ignore failures on cloud read-only filesystems)
                try:
                    with open(token_path, 'w') as token:
                        token.write(creds.to_json())
                except Exception:
                    pass
            except Exception as e:
                print(f"Error refreshing access token: {e}")
                creds = None
        
        if not creds:
            # 3. Check GMAIL_CREDENTIALS_JSON env variable (OAuth client config)
            env_creds = os.environ.get("GMAIL_CREDENTIALS_JSON")
            if env_creds:
                try:
                    client_config = json.loads(env_creds)
                    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                    if os.environ.get("RENDER"):
                        # We are on Render (headless cloud). run_local_server will fail.
                        raise RuntimeError(
                            "OAuth token is invalid or missing in headless production environment. "
                            "Please authenticate locally and set the GMAIL_TOKEN_JSON environment variable on Render."
                        )
                    print("Starting local server for OAuth flow (using GMAIL_CREDENTIALS_JSON)...")
                    creds = flow.run_local_server(host='127.0.0.1', port=8080)
                except Exception as e:
                    print(f"OAuth flow failed using GMAIL_CREDENTIALS_JSON: {e}")
                    raise e
            else:
                # 4. Fallback to local credentials.json file
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(
                        f"Google API credentials file not found at {os.path.abspath(credentials_path)}. "
                        "Please refer to the README.md or set GMAIL_CREDENTIALS_JSON / GMAIL_TOKEN_JSON environment variables."
                    )
                if os.environ.get("RENDER"):
                    raise RuntimeError(
                        "OAuth token is invalid or missing in headless production environment. "
                        "Please authenticate locally and set the GMAIL_TOKEN_JSON environment variable on Render."
                    )
                print("About to open browser for auth (using credentials.json)...")
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                print("Flow created, starting local server...")
                creds = flow.run_local_server(host='127.0.0.1', port=8080)
                print("Auth completed!")
                
            # Save the newly generated credentials locally
            if creds:
                try:
                    with open(token_path, 'w') as token:
                        token.write(creds.to_json())
                except Exception as e:
                    print(f"Could not save token.json file locally: {e}")
                    
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
