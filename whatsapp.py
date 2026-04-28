from flask import Flask, request
from dotenv import load_dotenv
import os
import requests

from data_manager import get_faq, log_unanswered_question
from ai_handler import get_ai_response

load_dotenv()

app = Flask(__name__)

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
OWNER_NUMBER = os.getenv('OWNER_WHATSAPP_NUMBER')

def send_whatsapp_msg(to, message):
    """Sends a WhatsApp message to a given number."""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        'Authorization': f'Bearer {WHATSAPP_TOKEN}',
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message},
    }
    requests.post(url, headers=headers, json=payload)

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """Meta calls this once to verify your webhook is real."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def receive_message():
    """Handles incoming WhatsApp messages."""
    data = request.get_json()

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        parent_number = message["from"]
        parent_message = message["text"]["body"]
    except (KeyError, IndexError):
        return "OK", 200

    faq_text = get_faq()
    response = get_ai_response(parent_message, faq_text)

    if response == "ESCALATE":
        send_whatsapp_msg(
            parent_number,
            "I've passed your message to the owner who will be in touch shortly!"
        )

        send_whatsapp_msg(
            OWNER_NUMBER,
            f"Unanswered question: {parent_number}: \n{parent_message}"
        )

        log_unanswered_question(parent_number, parent_message)
    else:
        send_whatsapp_msg(parent_number, message)

    return "OK", 200
