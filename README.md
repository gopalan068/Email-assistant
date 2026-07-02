# Mail Assist • AI Correspondence Assistant

Mail Assist is a local email triage assistant that helps you separate important emails from noise, auto-classify spam, compile a 2-minute morning digest of newsletters, and draft response templates using local ML classifiers and the Gemini API.

---

## Architecture
```
                     [ Gmail API ] 
                           |
                           v
                   [ fetch_emails.py ]  --> RAW Emails
                           |
                           v
                 [ spam_classifier.pkl ] --> Classical ML Spam Triage
                           |
                           v (If Ham)
                [ classify_importance.py ] --> LLM Batched Importance Categorization
                 |                      |
        (If Newsletter)            (If Work/Personal)
                 |                      |
                 v                      v
        [ generate_digest.py ]   [ api_server.py ] <-- GET /api/inbox
         (LLM Digest Generator)         |          <-- GET /api/digest
                 |                      |          <-- POST /api/sync
                 v                      |          <-- POST /api/draft-reply
         [ GET /api/digest ] <----------+
                 |
                 v
      [ mail_assistant.html ] <-- Rich editorial-newspaper styled UI
```

---

## Directory Structure
```
/mail-assist
  /models
    train_spam_classifier.py  # Offline script to train spam classifier on Enron Spam
    spam_classifier.pkl       # Serialized scikit-learn model + vectorizer
  /backend
    fetch_emails.py           # Gmail API client (OAuth2 desktop flow)
    spam_filter.py            # Spam classifier inference wrapper
    classify_importance.py    # Batched LLM importance classifier + pre-filtering
    generate_digest.py        # Newsletter summarization (Extractive-Abstractive)
    llm_client.py             # Provider-agnostic LLM interface (Gemini)
    api_server.py             # Flask backend API serving local cache & routes
  /frontend
    mail_assistant.html       # Triage Web Dashboard UI
  requirements.txt            # Python dependencies
  .env.example                # Config template
  README.md                   # This instruction guide
```

---

## Setup & Installation

### Step 1 — Prerequisites & Dependencies
1. Ensure Python 3.8+ is installed on your local computer.
2. Open your terminal in the project directory (`D:/mail-assist`) and run:
   ```bash
   pip install -r requirements.txt
   ```

### Step 2 — Configure Environment
1. Copy `.env.example` to a new file named `.env`:
   ```bash
   copy .env.example .env
   ```
2. Open `.env` and fill in your Gemini API key (generate one for free at [Google AI Studio](https://aistudio.google.com/)):
   ```env
   GEMINI_API_KEY=AIzaSyYourGeminiApiKeyHere
   ```

### Step 3 — Generate Google credentials.json (Gmail API Authentication)
To fetch emails from your actual Gmail inbox, you need to configure an OAuth 2.0 client via Google Cloud Console:

1. **Create Google Cloud Project**:
   * Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
   * Click the project dropdown at the top and select **New Project**. Name it `Mail Assist` and click **Create**.
2. **Enable Gmail API**:
   * In the search bar at the top, type `Gmail API`.
   * Select **Gmail API** from the results and click **Enable**.
3. **Configure OAuth Consent Screen**:
   * On the left sidebar menu, click **APIs & Services** > **OAuth consent screen**.
   * Select **User Type** as **External** and click **Create**.
   * Under **App information**:
     * App name: `Mail Assist`
     * User support email: Select your email.
     * Developer contact information: Enter your email.
   * Click **Save and Continue**.
   * Under **Scopes**:
     * Click **Add or Remove Scopes**.
     * Search for `gmail.readonly`. Select the checkbox for `https://www.googleapis.com/auth/gmail.readonly`.
     * Scroll down and click **Update**.
     * Click **Save and Continue**.
   * Under **Test Users** (CRITICAL):
     * Click **Add Users**.
     * Enter the exact Gmail address you want to fetch emails from. (Only added test accounts can log in during development).
     * Click **Save and Continue**, then review details and click **Back to Dashboard**.
4. **Create Client Credentials**:
   * Click on the **Credentials** tab in the left sidebar.
   * Click **+ Create Credentials** at the top and select **OAuth client ID**.
   * Set the **Application type** dropdown to **Desktop app**.
   * Set **Name** to `Mail Assist Client`.
   * Click **Create**. A modal will appear showing the Client ID.
5. **Download Credentials File**:
   * Under **OAuth 2.0 Client IDs**, find your new client and click the **Download JSON** icon (downward arrow).
   * Rename the downloaded file to exactly `credentials.json`.
   * Move or copy the file into your project root directory: `D:/mail-assist/credentials.json`.

---

## Running the Application

### 1. Train the Spam Classifier Offline
Run the offline training script to pull the cleaned Enron Spam dataset from Hugging Face, train the scikit-learn model, and save it:
```bash
python models/train_spam_classifier.py
```
This will output training metrics and save the classifier pickle to `models/spam_classifier.pkl`.

### 2. Start the Backend API Server
Start the local server:
```bash
python backend/api_server.py
```
The server will boot up and bind to `http://localhost:5000`. By default, it will load high-fidelity offline mockup database caches.

### 3. Open the Frontend UI
Double-click `frontend/mail_assistant.html` to open it in any web browser. 
* By default, it runs in **offline mode**, presenting the beautiful editorial mockup UI immediately.
* Click the **Sync Correspondence** (Sync) button in the upper-right corner.
* The first time you sync, your browser will open a Google Sign-In page. Log in using the **Test User Gmail Account** you added on the Google Console, click **Advanced** -> **Go to Mail Assist (unsafe)**, grant permissions, and close the tab once the verification succeeds.
* The dashboard will now sync in real-time, fetching your actual emails and categorizing them!

---

## API Documentation

### `GET /api/inbox`
Retrieves categorized emails (Important, Regular, and Spam) in the database.
* **Response format**: JSON Dictionary of email objects.

### `GET /api/digest`
Retrieves newsletter summaries compiled into extractive-abstractive bullets.
* **Response format**: JSON List of digest entries.

### `POST /api/sync`
Clears local caches, triggers Gmail API fetch, runs the local spam filter, runs the batched LLM importance analyzer, and regenerates newsletter summaries.
* **Response format**: Success or error indicator.

### `POST /api/draft-reply`
Generates a context-aware draft reply using the LLM for a given email.
* **Request format**: `{"id": "msg_id_here"}`
* **Response format**: `{"status": "success", "draft": "Draft text reply..."}`
