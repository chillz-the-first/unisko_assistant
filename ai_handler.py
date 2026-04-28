import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def get_ai_response(parent_message, faq_text):
    """
    Sends the parent's message and FAQ to Gemini.
    Returns an answer if found, or 'ESCALATE' if not.
    """

    model = genai.GenerativeModel("gemini-1.5-flash")

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

    response = model.generate_content(prompt)
    answer = response.text.strip()
    return answer.upper() if answer.upper() == "ESCALATE" else answer
