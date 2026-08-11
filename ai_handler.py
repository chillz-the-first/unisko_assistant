from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

# Create the client once when the app starts, not on every message
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_ai_response(parent_message, faq_text):
    """
    Sends the parent's message and FAQ to Gemini.
    Returns an answer if found, or 'ESCALATE' if not.
    If Gemini fails (quota, network), we also return 'ESCALATE'
    so the parent still gets a response and the owner is notified.
    """

    prompt = f"""
    You are a friendly assistant for a tutoring centre.
    Only answer questions using the FAQ below.
    If the question cannot be answered from the FAQ,
    reply with exactly one word: ESCALATE

    FAQ:
    {faq_text}

    Parent's message:
    {parent_message}
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )
        answer = response.text.strip()
    except Exception as e:
        print(f"Gemini error, escalating instead: {e}")
        return "ESCALATE"

    # Gemini sometimes adds punctuation or extra words around ESCALATE.
    # Treat any short reply containing the word as an escalation.
    cleaned = answer.upper().strip(" .!\"'")
    if "ESCALATE" in cleaned and len(cleaned) < 30:
        return "ESCALATE"

    return answer
