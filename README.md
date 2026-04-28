# Unisko Assistant 🤖

A WhatsApp chatbot for an after-school tutoring centre that answers parent FAQs using AI, escalates unanswered questions to the owner, and sends automated monthly payment reminders.

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
| Meta WhatsApp Cloud API | Sending and receiving WhatsApp messages (free) |
| Google Gemini API | AI responses to parent questions (free tier) |
| Google Sheets | FAQ storage, parent balances, unanswered question log |
| APScheduler | Monthly payment reminder scheduling |
| Render | Cloud hosting (free tier) |

---

## Project Structure

```
unisko_bot/
├── main.py              # Entry point — runs the app and scheduler
├── data_manager.py      # All Google Sheets reading and writing
├── ai_handler.py        # Gemini AI prompt and response logic
├── whatsapp.py          # WhatsApp webhook and message sending
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

### 5. Add your Google credentials
Place your `credentials.json` file in the project root. This file is gitignored and will never be uploaded to GitHub.

### 6. Run the app
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
   - **Start Command:** `python main.py`
5. Add all environment variables from your `.env` file under **Advanced → Environment Variables**
6. Deploy — Render will give you a URL like `https://unisko-bot.onrender.com`
7. Use this URL to complete the Meta WhatsApp webhook setup: `https://unisko-bot.onrender.com/webhook`

---

## Meta WhatsApp Webhook Setup

Once deployed, go to your Meta Developer App:

1. Navigate to **WhatsApp → Configuration**
2. Set the **Webhook URL** to `https://your-render-url.onrender.com/webhook`
3. Set the **Verify Token** to match your `VERIFY_TOKEN` environment variable
4. Subscribe to the **messages** webhook field

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
       /          \
     YES           NO (ESCALATE)
      |             |
   Reply to      1. Notify parent
   parent        2. Forward to owner
                 3. Log to Google Sheets
```

### Payment Reminder Flow
```
1st, 10th, 20th of every month at 6am
        ↓
Read ParentBalances sheet
        ↓
Filter rows where Payment Status = Unpaid
        ↓
Send WhatsApp reminder to each unpaid parent
```

---

## Notes

- The Render free tier sleeps after 15 minutes of inactivity — the first message after a quiet period may take ~30 seconds to respond
- The Meta WhatsApp temporary access token expires after 24 hours — set up a permanent token via a Meta System User for production use
- Update the `OWNER_WHATSAPP_NUMBER` in `.env` whenever the owner's contact changes