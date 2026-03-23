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

def generate_response(chat_history: list, personality: str, user_context: dict = None) -> str:
    """
    Generates a response from AI based on chat history, personality, and wellness context.
    """
    api_key = os.environ.get("GROQ_API_KEY") or os.environ.get("OPENAI_API_KEY")
    
    # Build System Prompt with Context
    base_prompt = PERSONALITY_PROMPTS.get(personality, PERSONALITY_PROMPTS["Friendly"])
    if user_context:
        context_str = "\n\nCURRENT USER DATA:\n"
        context_str += f"- DayScore: {user_context.get('total_score', 'N/A')}/100\n"
        context_str += f"- Steps Today: {user_context.get('steps', 0):,}\n"
        context_str += f"- Sleep: {user_context.get('sleep', 0)} hours\n"
        context_str += f"- Calories: {user_context.get('calories', 0)} kcal\n"
        context_str += "Please use this data to give specific, personalized wellness advice."
        system_prompt = base_prompt + context_str
    else:
        system_prompt = base_prompt

    if not api_key:
        # Fallback simulated response if no API key is present
        time.sleep(1.0)
        return _simulate_response(chat_history[-1]["content"], personality, user_context)
    
    try:
        # Determine Provider (Groq or OpenAI)
        if os.environ.get("GROQ_API_KEY"):
            client = OpenAI(
                api_key=os.environ.get("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1"
            )
            model = "llama-3.1-8b-instant"
        else:
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            model = "gpt-3.5-turbo" # Default lightweight model
        
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
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Oops! Having trouble connecting to my brain right now. ({str(e)})"


def _simulate_response(user_text, personality, context=None):
    """Fallback when no API key is configured with improved context awareness."""
    user_text = user_text.lower()
    
    data_mention = ""
    if context:
        data_mention = f" I see your DayScore is **{context.get('total_score', 0)}** today."
        if context.get('steps', 0) > 8000:
            data_mention += " Great job on those steps! 🚶"
        elif context.get('sleep', 0) < 6:
            data_mention += " You look a bit tired, maybe get some extra rest? 😴"

    msg = f"{data_mention}\n\nI'm currently in **Demo Mode** (no API key). To unlock my full AI potential, please add your `GROQ_API_KEY` or `OPENAI_API_KEY` to the `.env` file!"
    
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
