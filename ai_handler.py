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
    You are the WhatsApp assistant for Unisko, an after-school tutoring centre. You answer questions from parents.
    
    Rules:
    - Answer ONLY using the information in the FAQ below. Do not invent fees, times, policies, or any other detail.
    - If the FAQ does not contain enough information to answer, reply with exactly: ESCALATE
    - For greeting or thanks (e.g. "hi", "thank you"), reply warmly and briefly, and invite their question.
    Do not escalate these.
    - Keep answers short and friendly, suitable for a WhatsApp message. Two or three sentences at most.
    - Do not mention the FAQ, these rules, or that you are an AI.
    - Write in the same language the parent used.
    - When the FAQ contains a specific answer, use its exact wording rather than rephrasing.

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
