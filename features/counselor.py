"""
DayScore - Counselor Feature
Counselor page with AI counselor chat, counselor directory, and session booking.
"""

import streamlit as st
import html
from datetime import datetime, timedelta

from config.settings import AppConfig
from services.counselor_service import CounselorService
from services.journal_service import JournalService


def render_counselor():
    """Render the Counselor page with 3 tabs."""
    user = st.session_state.get("user", {})
    user_id = user.get("user_id", AppConfig.DEMO_USER_ID)

    counselor_service = CounselorService()

    # ── Header ─────────────────────────────────────────
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h1 style="margin:0; font-size:32px; font-weight:800;
            background: linear-gradient(90deg, #6C63FF, #4ECDC4);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🩺 Wellness Counselor
        </h1>
        <p style="color: rgba(255,255,255,0.5); margin-top:4px; font-size:15px;">
            Talk to an AI counselor, find professionals, or join a video session
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ───────────────────────────────────────────
    tab_chat, tab_find, tab_sessions = st.tabs([
        "💬 AI Counselor", "👥 Find a Counselor", "📅 My Sessions"
    ])

    with tab_chat:
        _render_ai_counselor(user_id, counselor_service)

    with tab_find:
        _render_counselor_directory(user_id, counselor_service)

    with tab_sessions:
        _render_sessions(user_id, counselor_service)


# ── Tab 1: AI Counselor Chat ──────────────────────────

def _render_ai_counselor(user_id: str, service: CounselorService):
    """Render the AI counselor chat interface."""

    # Intro card
    st.markdown("""
    <div class="metric-card" style="border-left: 4px solid #6C63FF;
        background: linear-gradient(135deg, rgba(108,99,255,0.12), rgba(78,205,196,0.06));">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
            <div style="font-size:40px;">🧑‍⚕️</div>
            <div>
                <div style="font-size:18px; font-weight:700; color:white;">Dr. Mira — AI Wellness Counselor</div>
                <div style="color:rgba(255,255,255,0.5); font-size:13px;">
                    CBT-trained • Supportive listening • Available 24/7
                </div>
            </div>
        </div>
        <div style="color:rgba(255,255,255,0.6); font-size:13px; margin-top:4px;">
            💙 Share what's on your mind. Everything here is private and confidential.
            For serious concerns, please consult a professional counselor.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize chat history
    if "counselor_chat" not in st.session_state:
        st.session_state["counselor_chat"] = [
            {
                "role": "assistant",
                "content": "Hello! I'm Dr. Mira, your AI wellness counselor. 💙 "
                           "I'm here to listen and support you. How are you feeling today? "
                           "You can share anything — I'm here for you.",
            }
        ]

    # Display chat messages
    chat_container = st.container(height=420)
    with chat_container:
        for msg in st.session_state["counselor_chat"]:
            role = msg["role"]
            if role == "assistant":
                with st.chat_message("assistant", avatar="🧑‍⚕️"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("user", avatar="💬"):
                    st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Share what's on your mind...", key="counselor_input")

    if user_input:
        # Add user message
        st.session_state["counselor_chat"].append({
            "role": "user",
            "content": user_input,
        })

        # Get mood context from journal
        mood_context = _get_mood_context(user_id)

        # Get AI response
        with st.spinner("Dr. Mira is thinking..."):
            response = service.get_ai_response(
                user_message=user_input,
                chat_history=st.session_state["counselor_chat"],
                mood_context=mood_context,
            )

        # Add assistant response
        st.session_state["counselor_chat"].append({
            "role": "assistant",
            "content": response,
        })

        st.rerun()

    # Quick action buttons
    st.markdown("---")
    st.markdown("**Quick Topics:**")
    qcols = st.columns(4)
    quick_topics = [
        ("😰 I'm feeling anxious", "I'm feeling really anxious today and I'm not sure why."),
        ("😔 I'm feeling low", "I've been feeling down lately and struggling to find motivation."),
        ("😫 Work stress", "I'm overwhelmed with work and can't seem to find balance."),
        ("😴 Can't sleep", "I've been having trouble sleeping and it's affecting my day."),
    ]
    for i, (label, message) in enumerate(quick_topics):
        with qcols[i]:
            if st.button(label, width="stretch", key=f"quick_{i}"):
                st.session_state["counselor_chat"].append({
                    "role": "user",
                    "content": message,
                })
                mood_context = _get_mood_context(user_id)
                response = service.get_ai_response(message, st.session_state["counselor_chat"], mood_context)
                st.session_state["counselor_chat"].append({
                    "role": "assistant",
                    "content": response,
                })
                st.rerun()


def _get_mood_context(user_id: str) -> dict:
    """Gather mood context from journal for personalized AI responses."""
    try:
        journal_service = JournalService()
        stats = journal_service.get_mood_stats(user_id, days=7)
        today_entry = journal_service.get_entry_for_today(user_id)
        streak = journal_service.get_journal_streak(user_id)

        context = {
            "trend": stats.get("trend", "unknown") if stats.get("has_data") else "unknown",
            "journal_streak": streak,
        }

        if today_entry:
            context["mood_emoji"] = today_entry.get("mood_emoji", "")
            context["mood_label"] = today_entry.get("mood_label", "")

        return context
    except Exception:
        return {}


# ── Tab 2: Counselor Directory ────────────────────────

def _render_counselor_directory(user_id: str, service: CounselorService):
    """Render the counselor directory with profile cards."""

    # Specialty filter
    specialties = ["All", "Anxiety", "Depression", "Stress", "Relationships",
                   "Mindfulness", "Youth", "Sleep"]
    selected_specialty = st.selectbox(
        "Filter by specialty",
        specialties,
        label_visibility="collapsed",
    )

    counselors = service.get_counselors(selected_specialty)

    if not counselors:
        st.info("No counselors found for this filter. Try a different specialty.")
        return

    for counselor in counselors:
        # Tags HTML
        tags_html = " ".join(
            f'<span style="background:rgba(108,99,255,0.15); color:rgba(255,255,255,0.7); '
            f'padding:2px 10px; border-radius:20px; font-size:11px;">{t}</span>'
            for t in counselor.get("tags", [])
        )

        st.markdown(f"""
        <div class="metric-card" style="margin-bottom:12px;">
            <div style="display:flex; gap:16px; align-items:flex-start;">
                <div style="font-size:48px; min-width:56px; text-align:center;">
                    {counselor.get('avatar', '👨‍⚕️')}
                </div>
                <div style="flex:1;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div style="font-size:18px; font-weight:700; color:white;">
                                {counselor.get('name', 'Unknown Counselor')}
                            </div>
                            <div style="color:#6C63FF; font-size:13px; font-weight:600;">
                                {counselor.get('title', 'Counselor')} • {counselor.get('experience', 'New')}
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <div style="color:#FFD93D; font-size:14px; font-weight:700;">
                                ⭐ {counselor.get('rating', '5.0')} <span style="color:rgba(255,255,255,0.4);
                                font-weight:400; font-size:12px;">({counselor.get('reviews', '0')})</span>
                            </div>
                            <div style="color:#4ECDC4; font-size:13px; font-weight:600;">
                                {counselor.get('price', '$0 / session')}
                            </div>
                        </div>
                    </div>
                    <div style="color:rgba(255,255,255,0.6); font-size:13px; margin:8px 0;">
                        {counselor.get('bio', 'A new counselor on DayScore.')}
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
                        <div>{tags_html}</div>
                        <div style="color:rgba(255,255,255,0.5); font-size:12px;">
                            🟢 {counselor.get('next_available', 'Available soon')}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Booking button
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button(f"📅 Book Session", key=f"book_{counselor['id']}", width="stretch"):
                st.session_state[f"booking_{counselor['id']}"] = True

        # Booking form (shown when button clicked)
        if st.session_state.get(f"booking_{counselor['id']}", False):
            with st.form(f"booking_form_{counselor['id']}"):
                st.markdown(f"**Book a session with {counselor['name']}**")

                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    session_date = st.date_input(
                        "Date",
                        min_value=datetime.now().date(),
                        value=datetime.now().date() + timedelta(days=1),
                        key=f"date_{counselor['id']}",
                    )
                with bcol2:
                    session_time = st.selectbox(
                        "Time",
                        ["9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM",
                         "3:00 PM", "4:00 PM", "5:00 PM", "6:00 PM"],
                        key=f"time_{counselor['id']}",
                    )

                session_type = st.radio(
                    "Session type",
                    ["🎥 Video Call", "💬 Text Chat"],
                    horizontal=True,
                    key=f"type_{counselor['id']}",
                )

                if st.form_submit_button("✅ Confirm Booking", width="stretch", type="primary"):
                    result = service.book_session(
                        user_id=user_id,
                        counselor_id=counselor["id"],
                        session_date=str(session_date),
                        session_time=session_time,
                        session_type="video" if "Video" in session_type else "chat",
                    )
                    if result.get("success"):
                        st.session_state[f"booking_{counselor['id']}"] = False
                        st.success(f"✅ Session booked with {counselor['name']}! Check 'My Sessions' for details.")
                        st.balloons()
                    else:
                        st.error("Failed to book session. Please try again.")

        st.markdown("")  # Spacer


# ── Tab 3: My Sessions ────────────────────────────────

def _render_sessions(user_id: str, service: CounselorService):
    """Render the user's booked sessions."""

    bookings = service.get_bookings(user_id)

    if not bookings:
        st.markdown("""
        <div class="metric-card" style="text-align:center; padding:48px;">
            <div style="font-size:64px; margin-bottom:16px;">📅</div>
            <h3 style="color:white; margin-bottom:8px;">No Sessions Yet</h3>
            <p style="color:rgba(255,255,255,0.5);">
                Browse the <strong>Find a Counselor</strong> tab to book your first session!
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"**{len(bookings)} session{'s' if len(bookings) != 1 else ''} booked**")

    for booking in bookings:
        session_type_icon = "🎥" if booking.get("session_type") == "video" else "💬"
        status_color = "#4ECDC4" if booking.get("status") == "confirmed" else "#FFD93D"

        st.markdown(f"""
        <div class="metric-card" style="margin-bottom:12px;
            border-left: 4px solid {status_color};">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <div style="font-size:36px;">{booking.get('counselor_avatar', '👩‍⚕️')}</div>
                    <div>
                        <div style="font-size:16px; font-weight:700; color:white;">
                            {booking.get('counselor_name', 'Counselor')}
                        </div>
                        <div style="color:rgba(255,255,255,0.5); font-size:13px;">
                            {booking.get('counselor_title', '')}
                        </div>
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="color:white; font-weight:600; font-size:15px;">
                        📅 {booking.get('session_date', '')}
                    </div>
                    <div style="color:rgba(255,255,255,0.5); font-size:13px;">
                        🕐 {booking.get('session_time', '')} • {session_type_icon}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Action buttons
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            meet_link = booking.get("meet_link", "")
            if meet_link and booking.get("session_type") == "video":
                st.link_button(
                    "🎥 Join Video Call",
                    meet_link,
                    width="stretch",
                    type="primary",
                )
            elif booking.get("session_type") == "chat":
                st.button("💬 Open Chat", key=f"chat_{booking.get('id', '')}", width="stretch")

        with col2:
            st.markdown(
                f'<div style="padding:8px; text-align:center; color:{status_color}; '
                f'font-weight:600; font-size:14px;">✅ {booking.get("status", "confirmed").title()}</div>',
                unsafe_allow_html=True,
            )

    # Emergency resources
    st.markdown("---")
    st.markdown("""
    <div class="metric-card" style="background: linear-gradient(135deg, rgba(255,107,107,0.1), rgba(255,140,66,0.05));
        border-left: 4px solid #FF6B6B;">
        <div style="font-size:16px; font-weight:700; color:white; margin-bottom:8px;">
            🆘 Crisis Resources
        </div>
        <div style="color:rgba(255,255,255,0.7); font-size:13px; line-height:1.8;">
            If you or someone you know is in immediate danger, please reach out:<br>
            📞 <strong>AASRA</strong>: 9820466726 (India)<br>
            📞 <strong>Vandrevala Foundation</strong>: 1860-2662-345 (India)<br>
            📞 <strong>National Suicide Prevention Lifeline</strong>: 988 (USA)<br>
            📞 <strong>Crisis Text Line</strong>: Text HOME to 741741 (USA)
        </div>
    </div>
    """, unsafe_allow_html=True)
