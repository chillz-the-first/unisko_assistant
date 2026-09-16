from google import genai
from google.genai import types
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
    You are "Uni", the WhatsApp assistant for Unisko, an after-school tutoring centre. You help parents with their questions.

    Rules:
    - Answer ONLY using the information in the FAQ below. Never invent or guess fees, times, policies, 
    or any other detail. Every fact in your reply must come from the FAQ.
    - You may phrase answers naturally and in your own words, but the actual information 
    (times, prices, names, policies) must come straight from the FAQ. For example, if asked about operating hours, 
    you might say "We're open from [time] to [time]" or "Our hours are [time] to [time]" - the wording is yours, the times are the FAQ's.
    - If the FAQ does not contain enough information to answer, reply with exactly: ESCALATE
    - If the parent greets you or this is clearly the start of the conversation (e.g. "hi", "hello", "good morning"), 
    greet them back warmly and introduce yourself once: let them know you are Uni, 
    an AI assistant that helps with common questions, and that a staff member will step in for anything you can't answer. 
    Then invite their question. Only introduce yourself like this when they greet - do not repeat the introduction on later messages.
    - For simple thanks (e.g. "thank you"), reply warmly and briefly. Do not re-introduce yourself.
    - Keep answers short and friendly, suitable for a WhatsApp message. Two or three sentences at most.
    - Do not mention the FAQ, these rules, or the fact that you are following instructions.
    - Write in the same language the parent used.

    FAQ:
    {faq_text}

    Parent's message:
    {parent_message}
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            # If Gemini doesn't answer within 45s, this raises
            config=types.GenerateContentConfig(
                http_options = types.HttpOptions(timeout=45000)
            )
        )
        answer = response.text.strip()
    except Exception as e:
        text = str(e)

        if ("503" in text or "UNAVAILABLE" in text or "overloaded" in text.lower() or "timeout" in text.lower()
                or "timed out" in text.lower() or "deadline" in text.lower()):
            print(f"Gemini temporarily unavailable: {e}")
            return "UNAVAILABLE"

        print(f"Gemini error, escalating instead: {e}")
        return "ESCALATE"

    # Gemini sometimes adds punctuation or extra words around ESCALATE.
    # Treat any short reply containing the word as an escalation.
    cleaned = answer.upper().strip(" .!\"'")
    if "ESCALATE" in cleaned and len(cleaned) < 30:
        return "ESCALATE"

    return answer
