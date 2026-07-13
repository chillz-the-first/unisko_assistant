from flask import Flask, request
from dotenv import load_dotenv
from collections import deque
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

GRAPH_URL = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"

# Meta sometimes delivers the same message twice (e.g. if a reply is slow).
# Remember the last 200 message IDs so we never answer the same message twice.
processed_ids = deque(maxlen=200)

def _post_to_whatsapp(payload):
    """Sends a payload to the WhatsApp API and logs any failure."""
    headers = {
        'Authorization': f'Bearer {WHATSAPP_TOKEN}',
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(GRAPH_URL, headers=headers, json=payload, timeout=15)
        if response.status_code >= 400:
            print(f"WhatsApp API error {response.status_code}: {response.text}")
            return False
        return True
    except requests.RequestException as e:
        print(f"WhatsApp API request failed: {e}")
        return False

def send_whatsapp_msg(to, message):
    """Sends a plain text WhatsApp message. Only works inside the 24-hour
    customer service window (i.e. replying to someone who messaged you)."""
    payload = {
        "messaging_product": "whatsapp",
        "to": str(to),
        "text": {"body": message},
    }
    return _post_to_whatsapp(payload)

def send_whatsapp_template(to, template_name, parameters, language="en"):
    """Sends an approved template message. Required for business-initiated
    messages (like payment reminders) outside the 24-hour window.
    `parameters` is a list of strings filling the template's {{1}}, {{2}}, ..."""
    payload = {
        "messaging_product": "whatsapp",
        "to": str(to),
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
            "components": [{
                "type": "body",
                "parameters": [{"type": "text", "text": str(p)} for p in parameters]
            }]
        }
    }
    return _post_to_whatsapp(payload)

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
    except (KeyError, IndexError, TypeError):
        # Not a message event (e.g. a delivery/read receipt) — ignore it
        return "OK", 200

    # Skip duplicates if Meta redelivers the same message
    message_id = message.get("id")
    if message_id in processed_ids:
        return "OK", 200
    processed_ids.append(message_id)

    # Voice notes, images and documents have no "text" field
    if message.get("type") != "text":
        send_whatsapp_msg(
            parent_number,
            "Sorry, I can only read typed messages at the moment. "
            "Please send your question as text."
        )
        return "OK", 200

    parent_message = message["text"]["body"]

    try:
        faq_text = get_faq()
        response = get_ai_response(parent_message, faq_text)
    except Exception as e:
        # If Sheets or anything else fails, escalate rather than go silent
        print(f"Error while processing message: {e}")
        response = "ESCALATE"

    if response == "ESCALATE":
        send_whatsapp_msg(
            parent_number,
            "I've passed your message to the owner who will be in touch shortly!"
        )

        send_whatsapp_msg(
            OWNER_NUMBER,
            f"Unanswered question: {parent_number}: \n{parent_message}"
        )

        try:
            log_unanswered_question(parent_number, parent_message)
        except Exception as e:
            print(f"Could not log unanswered question: {e}")
    else:
        send_whatsapp_msg(parent_number, response)

    return "OK", 200

from scheduler import start_scheduler
start_scheduler()
