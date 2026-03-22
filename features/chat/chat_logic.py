import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Dictionary to store system prompts based on personality
PERSONALITY_PROMPTS = {
    "Friendly": (
        "You are DayBot, a highly cheerful, warm, and supportive AI assistant for a wellness app called DayScore. "
        "Your goal is to help users and make them feel good. "
        "Always use a casual tone and include occasional emojis. 😊 Keep responses helpful, concise and empathetic."
    ),
    "Professional": (
        "You are DayBot, a professional, highly efficient AI assistant for the DayScore platform. "
        "Your goal is to provide clear, direct, and concise information. "
        "Always use a formal and respectful tone. Do not use emojis. Keep responses strictly focused on answering the user's questions."
    ),
    "Rude": (
        "You are DayBot, a slightly sarcastic, witty, but ultimately helpful AI assistant for DayScore. "
        "Your attitude is 'I can't believe I have to answer this, but here you go.' "
        "Use dry humor and controlled sarcasm, but NEVER be offensive, abusive, or refuse to help. "
        "Keep responses short and funny. Example tone: 'Oh great, another question. Fine, let me fix it for you...'"
    )
}

def generate_response(chat_history: list, personality: str) -> str:
    """
    Generates a response from OpenAI based on chat history and selected personality.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        # Fallback simulated response if no API key is present
        time.sleep(1.5)  # Simulate network latency
        return _simulate_response(chat_history[-1]["content"], personality)
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
        # Build the exact message list for the API
        system_prompt = PERSONALITY_PROMPTS.get(personality, PERSONALITY_PROMPTS["Friendly"])
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Append valid history (ignoring potentially invalid types that might have snuck in)
        for msg in chat_history:
            if msg.get("role") in ["user", "bot"]:
                messages.append({
                    "role": "assistant" if msg["role"] == "bot" else "user",
                    "content": msg.get("content", "")
                })
        
        # Make the API call
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # use a fast, free groq model
            messages=messages,
            temperature=0.7,
            max_tokens=250
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Oops! Having trouble connecting to my brain right now. ({str(e)})"


def _simulate_response(user_text, personality):
    """Fallback when no API key is configured."""
    user_text = user_text.lower()
    msg = "I'm currently in **Demo Mode** because no API key is connected. To make me smart and answer your questions, please add your `GROQ_API_KEY` or `OPENAI_API_KEY` to the `.env` file!"
    
    if personality == "Friendly":
        if "hello" in user_text or "hi" in user_text:
            return "Hey there! 😊 " + msg
        return f"That's a great question about '{user_text}'! 😊 Unfortunately, " + msg.lower()
        
    elif personality == "Professional":
        if "hello" in user_text or "hi" in user_text:
            return "Hello. " + msg
        return f"Regarding '{user_text}': " + msg
        
    else: # Rude
        if "hello" in user_text or "hi" in user_text:
            return "Oh, it's you. Look, " + msg.lower()
        return f"Seriously? You expect me to know about '{user_text}' without a brain? " + msg
