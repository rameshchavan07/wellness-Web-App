"""
DayScore - AI Chatbot Service
Wellness chatbot powered by OpenAI API.
"""

import streamlit as st
from datetime import datetime, timezone
from config.settings import OpenAIConfig
from config.firebase_config import get_firestore_client
from google.cloud.firestore_v1.base_query import FieldFilter


SYSTEM_PROMPT = """You are DayScore AI, a friendly and knowledgeable wellness assistant.
Your role is to:
- Suggest personalized workouts based on user fitness data
- Provide mental health tips and stress management advice
- Answer health and nutrition questions
- Motivate users to maintain healthy habits
- Offer sleep hygiene recommendations
- Suggest breathing exercises and mindfulness techniques

Important guidelines:
- Be supportive and encouraging, never judgmental
- Recommend professional help for serious health concerns
- Base suggestions on evidence-based health practices
- Keep responses concise but helpful (2-4 paragraphs max)
- Use emojis sparingly for a friendly tone
"""


class ChatbotService:
    """AI-powered wellness chatbot."""

    def __init__(self):
        self.api_key = OpenAIConfig.API_KEY
        self.model = OpenAIConfig.MODEL
        self.max_tokens = OpenAIConfig.MAX_TOKENS
        self.temperature = OpenAIConfig.TEMPERATURE
        self.db = get_firestore_client()

    def get_response(self, user_message: str, user_context: dict = None) -> str:
        """
        Get AI response for user message.

        Args:
            user_message: User's query
            user_context: Optional dict with user score/metrics for personalization

        Returns:
            AI response string
        """
        if not self.api_key:
            return self._get_fallback_response(user_message)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            # Add user context if available
            if user_context:
                context_msg = self._build_context_message(user_context)
                messages.append({"role": "system", "content": context_msg})

            # Add chat history from session state
            history = st.session_state.get("chat_history", [])
            for msg in history[-10:]:  # Last 10 messages for context
                messages.append({"role": msg["role"], "content": msg["content"]})

            messages.append({"role": "user", "content": user_message})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            return response.choices[0].message.content

        except Exception as e:
            return self._get_fallback_response(user_message)

    def save_chat_message(self, user_id: str, role: str, content: str):
        """Save chat message to Firestore."""
        try:
            if self.db:
                self.db.collection("chat_history").add({
                    "user_id": user_id,
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
        except Exception:
            pass

    def get_chat_history(self, user_id: str, limit: int = 50) -> list:
        """Retrieve recent chat history from Firestore."""
        try:
            if self.db:
                docs = (
                    self.db.collection("chat_history")
                    .where(filter=FieldFilter("user_id", "==", user_id))
                    .order_by("timestamp", direction="DESCENDING")
                    .limit(limit)
                    .stream()
                )
                messages = [doc.to_dict() for doc in docs]
                return list(reversed(messages))
            return []
        except Exception:
            return []

    @staticmethod
    def _build_context_message(context: dict) -> str:
        lines = ["Current user wellness data:"]
        if "total_score" in context:
            lines.append(f"- DayScore: {context['total_score']}/100")
        if "steps" in context:
            lines.append(f"- Steps today: {context['steps']}")
        if "sleep" in context:
            lines.append(f"- Sleep: {context['sleep']} hours")
        if "calories" in context:
            lines.append(f"- Calories burned: {context['calories']}")
        if "heart_rate" in context:
            lines.append(f"- Resting heart rate: {context['heart_rate']} BPM")
        lines.append("Use this data to personalize your response.")
        return "\n".join(lines)

    @staticmethod
    def _get_fallback_response(message: str) -> str:
        """Rule-based fallback when OpenAI is unavailable."""
        msg = message.lower()

        if any(w in msg for w in ["workout", "exercise", "training", "gym"]):
            return (
                "💪 **Here's a quick workout suggestion:**\n\n"
                "**Beginner (20 min):** 5 min warm-up walk → 10 bodyweight squats → "
                "10 push-ups → 20 jumping jacks → 30 sec plank → repeat 2x → 5 min cool-down stretch\n\n"
                "**Tip:** Start small and increase intensity gradually. "
                "Consistency matters more than intensity!"
            )
        elif any(w in msg for w in ["sleep", "insomnia", "rest", "tired"]):
            return (
                "😴 **Sleep Tips for Better Rest:**\n\n"
                "1. **Consistent schedule** — Go to bed and wake up at the same time daily\n"
                "2. **Screen-free zone** — No phones/laptops 30 min before bed\n"
                "3. **Cool & dark room** — Ideal temperature is 65-68°F (18-20°C)\n"
                "4. **Relaxation ritual** — Try the 4-7-8 breathing technique\n"
                "5. **Limit caffeine** — No coffee after 2 PM"
            )
        elif any(w in msg for w in ["stress", "anxiety", "mental", "calm", "relax"]):
            return (
                "🧘 **Stress Management Tips:**\n\n"
                "1. **Box breathing** — Inhale 4s → Hold 4s → Exhale 4s → Hold 4s\n"
                "2. **5-4-3-2-1 grounding** — Name 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste\n"
                "3. **Move your body** — Even a 10-minute walk can reduce stress hormones\n"
                "4. **Journaling** — Write down 3 things you're grateful for today\n\n"
                "Remember: It's okay to ask for professional support if you need it 💙"
            )
        elif any(w in msg for w in ["diet", "nutrition", "food", "eat", "meal"]):
            return (
                "🥗 **Nutrition Tips:**\n\n"
                "1. **Eat the rainbow** — Include colorful fruits and vegetables\n"
                "2. **Stay hydrated** — Aim for 8 glasses of water daily\n"
                "3. **Balanced meals** — Combine protein + complex carbs + healthy fats\n"
                "4. **Mindful eating** — Eat slowly and without screens\n"
                "5. **Meal prep** — Preparing meals ahead prevents unhealthy choices"
            )
        elif any(w in msg for w in ["walk", "steps", "running", "cardio"]):
            return (
                "🚶 **Walking & Cardio Tips:**\n\n"
                "• **Goal:** 10,000 steps/day (about 5 miles)\n"
                "• **Easy wins:** Take stairs, park farther away, walk during calls\n"
                "• **Interval walking:** Alternate 3 min brisk + 1 min normal pace\n"
                "• **Track progress:** Your DayScore rewards every step!\n\n"
                "Even 30 minutes of walking reduces heart disease risk by 19%! 🫀"
            )
        else:
            return (
                "👋 **Hi! I'm DayScore AI, your wellness companion.**\n\n"
                "I can help with:\n"
                "• 💪 Workout suggestions\n"
                "• 😴 Sleep tips\n"
                "• 🧘 Stress management\n"
                "• 🥗 Nutrition advice\n"
                "• 🚶 Activity recommendations\n\n"
                "What would you like to know about?"
            )
