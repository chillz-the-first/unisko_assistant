# Unisko Assistant 🤖

A WhatsApp automation system for an after-school tutoring centre that answers parent FAQs using AI, escalates unanswered questions to the owner, and sends automated monthly payment reminders.

---

## Features

- **FAQ Bot** — Parents can ask questions via WhatsApp and get instant AI-powered answers drawn from a Google Sheet
- **Escalation** — If a question can't be answered from the FAQ, the parent is notified and the owner receives the message on WhatsApp, with the question logged to a Google Sheet
- **Payment Reminders** — Automatically sends WhatsApp reminders to parents with outstanding balances on the 1st, 10th, and 20th of every month

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python + Flask | Web server that receives WhatsApp messages |
| Gunicorn | Production WSGI server |
| Meta WhatsApp Cloud API | Sending and receiving WhatsApp messages (free) |
| Google Gemini API (`gemini-2.5-flash`) | AI responses to parent questions (free tier) |
| Google Sheets | FAQ storage, parent balances, unanswered question log |
| APScheduler | Monthly payment reminder scheduling |
| Render | Cloud hosting (free tier) |

---

## Project Structure

```
unisko_bot/
├── main.py              # Entry point — runs the scheduler
├── data_manager.py      # All Google Sheets reading and writing
├── ai_handler.py        # Gemini AI prompt and response logic
├── whatsapp.py          # WhatsApp webhook, message sending, app entry point
├── requirements.txt     # Python dependencies
├── Procfile             # Render start command
├── .env.example         # Template for required environment variables
└── .gitignore           # Keeps secrets out of GitHub
```

---

## Google Sheets Setup

Three separate Google Sheets are required. Each must be shared with the service account email from your `credentials.json` file.

### 1. UniskoFAQ
Permission: **Viewer**

| Question | Answer |
|----------|--------|
| What are your fees? | Our fees are R500 per month per subject. |
| ... | ... |

### 2. ParentBalances
Permission: **Viewer**

| Parent Name | Parent WhatsApp | Student Name | Amount Due | Payment Status |
|-------------|----------------|--------------|------------|----------------|
| Sarah Jones | 27821234567 | Tom Jones | R500 | Unpaid |

### 3. UnansweredQuestions
Permission: **Editor**

| Timestamp | Parent Number | Question | Status |
|-----------|--------------|----------|--------|
| 2024-01-28 14:35:22 | 27821234567 | Do you offer Accounting? | Pending |

> ⚠️ UnansweredQuestions requires **Editor** permission because the bot writes new rows to it.

---

## Environment Variables

Create a `.env` file in the project root. **Never commit this file to GitHub.**

```
GEMINI_API_KEY=your_gemini_api_key
FAQ_SHEET_ID=your_faq_sheet_id
BALANCES_SHEET_ID=your_balances_sheet_id
UNANSWERED_SHEET_ID=your_unanswered_sheet_id
WHATSAPP_TOKEN=your_meta_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
VERIFY_TOKEN=your_chosen_verify_token
OWNER_WHATSAPP_NUMBER=27xxxxxxxxx
GOOGLE_CREDENTIALS={"type":"service_account", ...entire json content...}
```

> 💡 **Where is my Sheet ID?** Open your Google Sheet — the ID is the long string in the URL between `/d/` and `/edit`.
> Example: `docs.google.com/spreadsheets/d/`**`15Ewbw1GdWiMrkrvyQhlwNJhby_f1FBaGGCh6CnOudhs`**`/edit`

> 💡 **WhatsApp numbers** must be in international format with no `+` or spaces. South African numbers drop the leading `0` and add `27`. So `0821234567` becomes `27821234567`.

> 💡 **GOOGLE_CREDENTIALS** is needed both locally (in your `.env` file) and on Render (as an environment variable). Open your `credentials.json`, copy the entire contents, and paste it as one single line.

---

## Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/unisko_bot.git
cd unisko_bot
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your environment variables
Copy `.env.example` to `.env` and fill in all the values:
```bash
# Windows:
copy .env.example .env

# Mac/Linux:
cp .env.example .env
```

### 5. Run the app
```bash
python main.py
```

---

## Deployment (Render)

1. Push your code to GitHub (`.env` and `credentials.json` are gitignored automatically)
2. Go to [render.com](https://render.com) and create a new **Web Service**
3. Connect your GitHub repository
4. Set the following:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn whatsapp:app`
5. Add all environment variables from your `.env` file under **Advanced → Environment Variables**
6. Deploy — Render will give you a URL like `https://unisko-bot.onrender.com`
7. Use this URL to complete the Meta WhatsApp webhook setup: `https://unisko-bot.onrender.com/webhook`

> ⚠️ If Render shows a start command field that can't be left blank, enter `gunicorn whatsapp:app` directly in the dashboard rather than relying on the Procfile.

---

## Meta WhatsApp Webhook Setup

Once deployed, go to your Meta Developer App:

1. Navigate to **WhatsApp → Configuration**
2. Set the **Webhook URL** to `https://your-render-url.onrender.com/webhook`
3. Set the **Verify Token** to match your `VERIFY_TOKEN` environment variable
4. Subscribe to the **messages** webhook field
5. In **WhatsApp → Getting Started**, add your personal WhatsApp number to the test recipients list — Meta only allows messages to verified numbers until your app is fully approved

---

## How It Works

### FAQ Bot Flow
```
Parent sends WhatsApp message
        ↓
Meta Cloud API forwards to /webhook
        ↓
Flask receives the message
        ↓
Reads FAQ from Google Sheets
        ↓
Sends FAQ + message to Gemini AI
        ↓
        Can Gemini answer?
       /                   \
     YES                    NO (ESCALATE)
      |                      |
   Reply to            1. Reply to parent:
   parent                 "I've passed your message
                           to the owner who will be
                           in touch shortly!"
                        2. Forward message to owner
                           on WhatsApp
                        3. Log to UnansweredQuestions
                           sheet with status "Pending"
```

### Payment Reminder Flow
```
1st, 10th, 20th of every month at 6am UTC (8am SAST)
        ↓
Read ParentBalances sheet
        ↓
Filter rows where Payment Status = Unpaid
        ↓
Send WhatsApp reminder to each unpaid parent
(deadline adjusts per reminder: 8th, 17th, 27th)
```

---

## Known Limitations

| Limitation | Detail |
|-----------|--------|
| **Render free tier sleeps** | The service sleeps after 15 minutes of inactivity. The first message after a quiet period may take ~30 seconds to respond as the server wakes up |
| **Meta 1,000 conversation limit** | The free WhatsApp Cloud API allows up to 1,000 conversations per month. For a small tutoring centre this is more than enough, but worth monitoring |
| **Meta temporary access token** | The WhatsApp token from the Getting Started page expires after 24 hours. For permanent use, set up a System User token via Meta Business Settings |
| **Gemini free tier rate limits** | `gemini-2.5-flash` on the free tier has limits on requests per minute and per day. For a small centre this is sufficient, but high message volumes could hit limits |
| **No message history** | The bot has no memory of previous messages in a conversation. Each message is treated independently |
| **Text messages only** | The bot currently only handles text messages. Voice notes, images, or documents sent by parents will be ignored |
| **Scheduler timezone** | APScheduler runs in UTC by default. South Africa is UTC+2, so the 6am scheduled time fires at 8am SAST — which is intentional, but worth knowing if you change the schedule |

---

## Troubleshooting

A log of real errors encountered during development and how to fix them.

---

### `scikit-learn` or `scipy` build failure on Render
**Error:** `ERROR: Failed to build 'scikit-learn'` or `metadata-generation-failed`

**Cause:** Running `pip freeze` captures every library installed in your virtual environment, including heavy data science libraries unrelated to the project.

**Fix:** Replace the entire contents of `requirements.txt` with only the libraries the project actually needs:
```
flask
google-auth
google-auth-oauthlib
google-api-python-client
google-genai
gspread
requests
apscheduler
python-dotenv
gunicorn
```

---

### Render running `python main.py` instead of `gunicorn`
**Symptom:** App starts with `python main.py` and crashes or shows a development server warning.

**Cause:** Render has a cached start command in the dashboard that overrides the Procfile.

**Fix:** Go to Render → Settings → Start Command and enter `gunicorn whatsapp:app` directly.

---

### `FutureWarning: google.generativeai package has ended`
**Cause:** The old `google-generativeai` library has been retired by Google.

**Fix:**
- Replace `google-generativeai` with `google-genai` in `requirements.txt`
- Update `ai_handler.py` to use the new syntax:
```python
from google import genai
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)
```

---

### `429 RESOURCE_EXHAUSTED` — Gemini quota exceeded
**Error:** `ClientError: 429 RESOURCE_EXHAUSTED, limit: 0, model: gemini-2.0-flash`

**Cause:** `gemini-2.0-flash` is deprecated and no longer available on the free tier.

**Fix:** Update the model name in `ai_handler.py`:
```python
model="gemini-2.5-flash"
```

---

### `404 NOT_FOUND` — Gemini model not found
**Error:** `ClientError: 404 NOT_FOUND, models/gemini-1.5-flash is not found for API version v1beta`

**Cause:** `gemini-1.5-flash` is no longer supported in the new `google-genai` SDK. The `models/` prefix is also not needed in the new SDK.

**Fix:** Update the model name in `ai_handler.py`:
```python
model="gemini-2.5-flash"  # No "models/" prefix needed
```

---

### Messages arriving but bot not replying
**Symptom:** Render logs show incoming POST requests but no WhatsApp reply is sent.

**Things to check:**
1. `WHATSAPP_TOKEN` in your environment variables is correct and not expired
2. `WHATSAPP_PHONE_NUMBER_ID` matches the number in your Meta dashboard
3. The recipient's number is added to Meta's test recipients list (required until the app is approved)
4. Check Render logs for any Python errors after the incoming request line

---

### Webhook verification failing
**Symptom:** Meta shows an error when trying to verify your webhook URL.

**Things to check:**
1. Your Render service is live and not sleeping — visit the URL in a browser first to wake it up
2. The `VERIFY_TOKEN` in Render's environment variables exactly matches what you entered in Meta's webhook form
3. The webhook URL ends in `/webhook` — e.g. `https://unisko-bot.onrender.com/webhook`

---

### Business portfolio required error on Meta
**Symptom:** Meta blocks WhatsApp setup with "In order to onboard onto the WhatsApp Business Platform, a business portfolio needs to be created."

**Fix:** Click "Create a business portfolio" and complete the Meta Business Suite setup. You do not need full business verification for testing — look for a "Skip" or "Continue" option if prompted to verify.