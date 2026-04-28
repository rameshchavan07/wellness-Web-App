"""
DayScore - Counselor Service
Manages counselor profiles, session booking, AI counselor chat, and video call links.
"""

import streamlit as st
import uuid
import random
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta, timezone
from config.settings import OpenAIConfig, SMTPConfig
from config.firebase_config import get_firestore_client
from google.cloud.firestore_v1.base_query import FieldFilter


# ── AI Counselor System Prompt ─────────────────────────
COUNSELOR_SYSTEM_PROMPT = """You are Dr. Mira, a compassionate and professional AI wellness counselor within the DayScore app.

Your approach:
- Use evidence-based Cognitive Behavioral Therapy (CBT) techniques
- Practice active listening — reflect back what the user says before responding
- Ask thoughtful follow-up questions to understand their feelings deeply
- Offer practical coping strategies and exercises
- Validate emotions without dismissing them
- Encourage journaling, mindfulness, and physical activity
- Always recommend seeking a professional if issues are serious (suicidal thoughts, severe anxiety, trauma)

Your style:
- Warm, empathetic, and non-judgmental
- Use "I hear you", "That sounds challenging", "It makes sense that you feel..."
- Keep responses focused and supportive (3-5 sentences)
- End with either a reflection question or a small actionable suggestion
- Use emojis sparingly and tastefully

IMPORTANT: You are NOT a replacement for a real therapist. If the user describes a crisis, gently direct them to emergency services or suggest booking with a real counselor using the "Find a Counselor" tab.

{user_context}
"""

# ── Sample Counselor Directory ─────────────────────────
COUNSELOR_PROFILES = [
    {
        "id": "dr_sharma",
        "name": "Dr. Priya Sharma",
        "email": "dr.sharma@dayscore.app",
        "title": "Clinical Psychologist",
        "specialty": "Anxiety & Stress Management",
        "experience": "12 years",
        "rating": 4.9,
        "reviews": 234,
        "avatar": "👩‍⚕️",
        "bio": "Specializes in cognitive behavioral therapy for anxiety disorders and workplace stress. Warm, structured approach.",
        "languages": ["English", "Hindi"],
        "next_available": "Tomorrow, 10:00 AM",
        "price": "₹800 / session",
        "tags": ["CBT", "Anxiety", "Stress", "Burnout"],
    },
    {
        "id": "dr_patel",
        "name": "Dr. Rohan Patel",
        "email": "dr.patel@dayscore.app",
        "title": "Psychiatrist",
        "specialty": "Depression & Mood Disorders",
        "experience": "15 years",
        "rating": 4.8,
        "reviews": 189,
        "avatar": "👨‍⚕️",
        "bio": "Expert in mood disorders with an integrative approach combining therapy and lifestyle medicine.",
        "languages": ["English", "Gujarati"],
        "next_available": "Today, 6:00 PM",
        "price": "₹1,200 / session",
        "tags": ["Depression", "Mood", "Medication", "Holistic"],
    },
    {
        "id": "ms_nair",
        "name": "Ananya Nair",
        "email": "ananya.nair@dayscore.app",
        "title": "Licensed Therapist",
        "specialty": "Relationships & Self-Esteem",
        "experience": "8 years",
        "rating": 4.9,
        "reviews": 312,
        "avatar": "👩‍💼",
        "bio": "Focuses on relationship dynamics, self-worth, and personal growth using person-centered therapy.",
        "languages": ["English", "Malayalam", "Hindi"],
        "next_available": "Tomorrow, 2:00 PM",
        "price": "₹600 / session",
        "tags": ["Relationships", "Self-Esteem", "Growth", "Empathy"],
    },
    {
        "id": "dr_khan",
        "name": "Dr. Ayesha Khan",
        "email": "dr.khan@dayscore.app",
        "title": "Child & Adolescent Psychologist",
        "specialty": "Youth Mental Health",
        "experience": "10 years",
        "rating": 4.7,
        "reviews": 156,
        "avatar": "👩‍🔬",
        "bio": "Passionate about helping young people navigate academic pressure, social media stress, and identity issues.",
        "languages": ["English", "Urdu", "Hindi"],
        "next_available": "Thursday, 11:00 AM",
        "price": "₹700 / session",
        "tags": ["Youth", "Academic Stress", "Social Media", "Identity"],
    },
    {
        "id": "mr_das",
        "name": "Siddharth Das",
        "email": "siddharth.das@dayscore.app",
        "title": "Mindfulness Coach",
        "specialty": "Meditation & Mindfulness",
        "experience": "6 years",
        "rating": 4.8,
        "reviews": 198,
        "avatar": "🧘‍♂️",
        "bio": "Certified mindfulness instructor combining ancient meditation practices with modern neuroscience.",
        "languages": ["English", "Bengali", "Hindi"],
        "next_available": "Today, 8:00 PM",
        "price": "₹500 / session",
        "tags": ["Mindfulness", "Meditation", "Sleep", "Relaxation"],
    },
]


class CounselorService:
    """Manages counselor features: directory, bookings, AI chat, and video links."""

    def __init__(self):
        self.db = get_firestore_client()
        self.api_key = OpenAIConfig.API_KEY

    # ── Counselor Directory ────────────────────────────

    def get_counselors(self, specialty_filter: str | None = None) -> list:
        """Get list of available counselors from Firestore, optionally filtered by specialty."""
        counselors = []
        try:
            if self.db:
                docs = self.db.collection("counselors").stream()
                counselors = [doc.to_dict() for doc in docs]
        except Exception:
            pass

        # Fallback to static list if Firestore fails or is empty
        if not counselors:
            counselors = COUNSELOR_PROFILES

        if specialty_filter and specialty_filter != "All":
            filter_str = str(specialty_filter).lower()
            counselors = [
                c for c in counselors
                if filter_str in str(c.get("specialty", "")).lower()
                or any(filter_str in str(tag).lower() for tag in c.get("tags", []))
            ]
        return counselors

    def get_counselor_by_id(self, counselor_id: str) -> dict:
        """Get a specific counselor by ID from Firestore."""
        try:
            if self.db:
                doc = self.db.collection("counselors").document(counselor_id).get()
                if doc.exists:
                    return doc.to_dict()
        except Exception:
            pass
            
        for c in COUNSELOR_PROFILES:
            if c.get("id") == counselor_id:
                return c
        return {}

    def get_counselor_by_email(self, email: str) -> dict:
        """Get a specific counselor by email from Firestore."""
        try:
            if self.db:
                docs = self.db.collection("counselors").where("email", "==", email).limit(1).stream()
                for doc in docs:
                    return doc.to_dict()
        except Exception:
            pass
            
        for c in COUNSELOR_PROFILES:
            if c.get("email", "").lower() == email.lower():
                return c
        return {}

    # ── Session Booking ────────────────────────────────

    def book_session(self, user_id: str, counselor_id: str,
                     session_date: str, session_time: str,
                     session_type: str = "video") -> dict:
        """Book a session with a counselor."""
        counselor = self.get_counselor_by_id(counselor_id)
        if not counselor:
            return {"success": False, "error": "Counselor not found"}

        # Generate a unique meeting link
        meet_link = self.generate_meet_link()

        booking = {
            "id": str(uuid.uuid4())[:8],
            "user_id": user_id,
            "counselor_id": counselor_id,
            "counselor_name": counselor.get("name", "Unknown Counselor"),
            "counselor_title": counselor.get("title", "Counselor"),
            "counselor_avatar": counselor.get("avatar", "👨‍⚕️"),
            "session_date": session_date,
            "session_time": session_time,
            "session_type": session_type,
            "meet_link": meet_link,
            "status": "confirmed",
            "booked_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            if self.db:
                self.db.collection("counselor_bookings").document(booking["id"]).set(booking)
            else:
                self._demo_book(booking)
        except Exception as e:
            st.warning(f"Could not save booking: {e}")
            self._demo_book(booking)

        # Send simulated email
        self._send_booking_email(user_id, booking)
        
        return {"success": True, "booking": booking}

    def _send_booking_email(self, user_id: str, booking: dict):
        """Send an actual email to the user with the meeting link."""
        user = st.session_state.get("user", {})
        email_address = user.get("email")
        
        if not email_address:
            st.warning("⚠️ No email associated with this account. Cannot send meeting link.")
            return

        # Prepare email content
        msg = EmailMessage()
        msg['Subject'] = f"Confirmed: Your Wellness Session with {booking['counselor_name']}"
        msg['From'] = SMTPConfig.FROM_EMAIL
        msg['To'] = email_address
        
        body = f"""
Hello!

Your wellness session has been successfully booked.

📅 Date: {booking['session_date']}
🕐 Time: {booking['session_time']}
🧑‍⚕️ Counselor: {booking['counselor_name']} ({booking['counselor_title']})

🔗 Join your session here:
{booking['meet_link']}

Thank you for prioritizing your mental health with DayScore.
"""
        msg.set_content(body)

        if not SMTPConfig.USERNAME or not SMTPConfig.PASSWORD:
            st.info(f"📧 Simulated email sent to {email_address} (SMTP credentials not configured in .env)")
            print(f"[SIMULATED EMAIL] To: {email_address}\n{body}")
            return

        try:
            with smtplib.SMTP(SMTPConfig.SERVER, SMTPConfig.PORT) as server:
                server.starttls()
                server.login(SMTPConfig.USERNAME, SMTPConfig.PASSWORD)
                server.send_message(msg)
            st.toast(f"📧 Meeting link sent to {email_address}", icon="✅")
        except Exception as e:
            st.error(f"Failed to send email: {str(e)}")
            print(f"[EMAIL ERROR]: {e}")

    def get_bookings(self, user_id: str) -> list:
        """Get all bookings for a user."""
        try:
            if self.db:
                docs = (
                    self.db.collection("counselor_bookings")
                    .where(filter=FieldFilter("user_id", "==", user_id))
                    .get()
                )
                bookings = [doc.to_dict() for doc in docs]
                bookings.sort(key=lambda x: x.get("session_date", ""), reverse=True)
                if bookings:
                    return bookings
            return st.session_state.get("demo_bookings", [])
        except Exception:
            return st.session_state.get("demo_bookings", [])

    def get_counselor_bookings(self, counselor_id: str) -> list:
        """Get all bookings for a counselor."""
        try:
            if self.db:
                docs = (
                    self.db.collection("counselor_bookings")
                    .where(filter=FieldFilter("counselor_id", "==", counselor_id))
                    .get()
                )
                bookings = [doc.to_dict() for doc in docs]
                bookings.sort(key=lambda x: x.get("session_date", ""), reverse=True)
                return bookings
            
            # For demo
            demo_bookings = st.session_state.get("demo_bookings", [])
            return [b for b in demo_bookings if b.get("counselor_id") == counselor_id]
        except Exception:
            return []

    # ── AI Counselor Chat ──────────────────────────────

    def get_ai_response(self, user_message: str, chat_history: list,
                        mood_context: dict = None) -> str:
        """Get a response from the AI counselor."""
        # Build context from mood data
        context_str = ""
        if mood_context:
            context_str = f"""
User context from DayScore app:
- Current mood: {mood_context.get('mood_emoji', 'Unknown')} ({mood_context.get('mood_label', 'Unknown')})
- Recent mood trend: {mood_context.get('trend', 'stable')}
- DayScore: {mood_context.get('day_score', 'N/A')}/100
- Journal streak: {mood_context.get('journal_streak', 0)} days
"""

        system_prompt = COUNSELOR_SYSTEM_PROMPT.format(user_context=context_str)

        # Try OpenAI/Groq API
        if self.api_key:
            try:
                return self._call_api(system_prompt, user_message, chat_history)
            except Exception:
                pass

        # Fallback to rule-based responses
        return self._rule_based_response(user_message)

    def _call_api(self, system_prompt: str, user_message: str, chat_history: list) -> str:
        """Call OpenAI/Groq API for AI counselor response."""
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=OpenAIConfig.API_KEY,
                base_url=OpenAIConfig.BASE_URL if hasattr(OpenAIConfig, 'BASE_URL') else None,
            )

            messages = [{"role": "system", "content": system_prompt}]

            # Add recent chat history (last 10 messages)
            for msg in chat_history[-10:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

            messages.append({"role": "user", "content": user_message})

            response = client.chat.completions.create(
                model=OpenAIConfig.MODEL,
                messages=messages,
                max_tokens=OpenAIConfig.MAX_TOKENS,
                temperature=0.7,
            )
            return response.choices[0].message.content

        except Exception as e:
            return self._rule_based_response(user_message)

    @staticmethod
    def _rule_based_response(message: str) -> str:
        """Provide therapeutic responses without API."""
        msg = message.lower()

        if any(w in msg for w in ["anxious", "anxiety", "worried", "panic", "nervous"]):
            return (
                "I hear that you're feeling anxious, and that's completely valid. 💙 "
                "Anxiety often comes from our mind trying to protect us from perceived threats. "
                "Let's try a quick grounding exercise: Name 5 things you can see, 4 you can touch, "
                "3 you can hear, 2 you can smell, and 1 you can taste. "
                "This can help bring you back to the present moment. Would you like to try it together?"
            )

        if any(w in msg for w in ["sad", "depressed", "hopeless", "crying", "unhappy"]):
            return (
                "I'm really sorry you're going through this. It takes courage to express how you feel. 💙 "
                "Sadness is a natural emotion, and it's okay to sit with it for a while. "
                "Sometimes, even a small act — like going for a short walk, calling a friend, "
                "or writing in your journal — can help shift your energy. "
                "What's one small thing you could do for yourself right now?"
            )

        if any(w in msg for w in ["stress", "overwhelm", "burnout", "exhausted", "tired"]):
            return (
                "It sounds like you're carrying a heavy load right now. That must be really tough. 🫂 "
                "When we're overwhelmed, our bodies hold tension. Try this: take a slow, deep breath in "
                "for 4 counts, hold for 4, and release for 6. Repeat 3 times. "
                "Also, consider making a list of what's on your plate — sometimes just writing things down "
                "makes them feel more manageable. What's the biggest stressor right now?"
            )

        if any(w in msg for w in ["sleep", "insomnia", "can't sleep", "nightmare"]):
            return (
                "Sleep struggles can be so frustrating. Your body needs rest, and it's understandable "
                "to feel distressed when it's hard to come by. 🌙 "
                "A few things that might help: try a consistent bedtime routine, avoid screens 30 minutes "
                "before bed, and try the 4-7-8 breathing technique (inhale 4s, hold 7s, exhale 8s). "
                "Have you noticed any patterns in what keeps you awake?"
            )

        if any(w in msg for w in ["angry", "frustrated", "irritated", "rage"]):
            return (
                "Anger is a valid emotion — it often tells us that a boundary has been crossed. 💪 "
                "It's great that you're acknowledging it instead of pushing it away. "
                "When anger rises, try the STOP technique: Stop, Take a breath, Observe what you're "
                "feeling, and Proceed with awareness. "
                "Would you like to talk about what triggered this feeling?"
            )

        if any(w in msg for w in ["lonely", "alone", "isolated", "no friends"]):
            return (
                "Feeling lonely can be incredibly painful, and I want you to know you're not alone in this. 💙 "
                "Connection is a basic human need. Even small connections matter — a chat with a neighbor, "
                "joining an online community, or volunteering. "
                "You've already taken a positive step by reaching out here. "
                "What's one way you could connect with someone this week?"
            )

        if any(w in msg for w in ["thank", "helpful", "better", "good"]):
            return (
                "I'm really glad to hear that! 😊 Remember, progress isn't always linear — "
                "there will be ups and downs, and that's perfectly normal. "
                "The fact that you're investing in your mental health is something to be proud of. "
                "Keep checking in with yourself, and I'm always here when you need to talk. 💙"
            )

        # Default empathetic response
        responses = [
            "Thank you for sharing that with me. 💙 It takes courage to open up. "
            "Can you tell me more about how that makes you feel? Understanding our emotions "
            "is the first step toward managing them.",

            "I appreciate you telling me this. 🌟 Sometimes just putting our thoughts into words "
            "can help us see things more clearly. What do you think is at the heart of this feeling?",

            "I hear you, and what you're experiencing sounds important. 💙 "
            "Let's explore this together — when did you first start noticing these feelings? "
            "Sometimes understanding the timeline can give us useful insights.",
        ]
        return random.choice(responses)

    # ── Video Call Link ────────────────────────────────

    @staticmethod
    def generate_meet_link() -> str:
        """Generate a working Jitsi Meet video call link."""
        code = uuid.uuid4().hex[:12]
        # Jitsi allows instant, free video calls without an API key
        return f"https://meet.jit.si/DayScoreSession_{code}"

    # ── Demo Mode Helpers ──────────────────────────────

    @staticmethod
    def _demo_book(booking: dict) -> dict:
        """Save booking to session state for demo mode."""
        if "demo_bookings" not in st.session_state:
            st.session_state["demo_bookings"] = []
        st.session_state["demo_bookings"].insert(0, booking)
        return {"success": True, "booking": booking}
