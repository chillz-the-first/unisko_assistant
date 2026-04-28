from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

def get_ai_response(parent_message, faq_text):
    """
    Sends the parent's message and FAQ to Gemini.
    Returns an answer if found, or 'ESCALATE' if not.
    """

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )
    answer = response.text.strip()
    return answer.upper() if answer.upper() == "ESCALATE" else answer
