import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os
from datetime import datetime
import json

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly"
]

def get_google_client():
    """Creates and returns an authorised Google Sheets client."""
    cred_json = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
    creds = Credentials.from_service_account_info(cred_json, scopes=SCOPES)
    return gspread.authorize(creds)

def get_faq():
    """Reads the FAQ sheet and returns a formatted string of Q&A pairs."""
    client = get_google_client()
    sheet = client.open_by_key(os.getenv("FAQ_SHEET_ID")).sheet1
    rows = sheet.get_all_records()

    faq_text = ""
    for row in rows:
        faq_text += f"Q: {row['Question']}\nA: {row['Answer']}\n\n"

    return faq_text


def log_unanswered_question(parent_number, question):
    """Logs an unanswered question to the UnansweredQuestions sheet."""
    client = get_google_client()
    sheet = client.open_by_key(os.getenv("UNANSWERED_SHEET_ID")).sheet1

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheet.append_row([timestamp, parent_number, question, "Pending"])

def get_unpaid_balances():
    client = get_google_client()
    sheet = client.open_by_key(os.getenv("BALANCES_SHEET_ID")).sheet1
    rows = sheet.get_all_records()

    unpaid_balances = []
    for row in rows:
        if row["Payment Status"] == "Unpaid":
            unpaid_balances.append(row)

    return unpaid_balances

