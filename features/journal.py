"""
DayScore - Mood Journal Feature
Daily mood journaling page with mood selector, gratitude prompts, free-text reflection, and entry timeline.
"""

import streamlit as st
import html
from datetime import datetime

from config.settings import AppConfig
from services.journal_service import JournalService, MOOD_SCALE, EMOTION_TAGS


def render_journal():
    """Render the Mood Journal page."""
    user = st.session_state.get("user", {})
    user_id = user.get("user_id", AppConfig.DEMO_USER_ID)

    journal_service = JournalService()

    # ── Header ─────────────────────────────────────────
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h1 style="margin:0; font-size:32px; font-weight:800;
            background: linear-gradient(90deg, #6C63FF, #4ECDC4);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            📓 Mood Journal
        </h1>
        <p style="color: rgba(255,255,255,0.5); margin-top:4px; font-size:15px;">
            Reflect on your day, track your emotions, and practice gratitude
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Journal Streak ─────────────────────────────────
    streak = journal_service.get_journal_streak(user_id)
    st.markdown(f"""
    <div class="metric-card" style="text-align:center; margin-bottom:24px;
        background: linear-gradient(135deg, rgba(108,99,255,0.15), rgba(78,205,196,0.1));">
        <div style="display:flex; justify-content:center; align-items:center; gap:24px;">
            <div>
                <span style="font-size:36px;">📝</span>
                <span style="font-size:28px; font-weight:800; color:#FFD93D; margin-left:8px;">{streak}</span>
                <span style="color:rgba(255,255,255,0.6); font-size:14px; margin-left:4px;">Day Journal Streak</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Check for existing entry today ─────────────────
    today_entry = journal_service.get_entry_for_today(user_id)

    # ── Today's Entry Form ─────────────────────────────
    st.markdown("### ✍️ Today's Reflection")

    if today_entry:
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid #4ECDC4;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div>
                    <span style="font-size:32px;">{today_entry.get('mood_emoji', '😊')}</span>
                    <span style="font-weight:700; color:white; margin-left:8px; font-size:18px;">
                        {today_entry.get('mood_label', 'Good')}
                    </span>
                </div>
                <span style="color:#4ECDC4; font-weight:600; font-size:14px;">✅ Logged Today</span>
            </div>
            <div style="color:rgba(255,255,255,0.7); font-size:14px; margin-bottom:8px;">
                {html.escape(today_entry.get('journal_text', '')[:200])}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if today_entry.get("gratitude"):
            st.markdown("**🙏 Today's Gratitude:**")
            for g in today_entry["gratitude"]:
                st.markdown(f"- {html.escape(g)}")

        if st.button("📝 Edit Today's Entry", width="stretch"):
            st.session_state["journal_editing"] = True
            st.rerun()

        show_form = st.session_state.get("journal_editing", False)
    else:
        show_form = True

    if show_form:
        with st.form("journal_entry_form", clear_on_submit=False):
            # Mood Selector
            st.markdown("**How are you feeling today?**")
            mood_cols = st.columns(5)
            mood_emojis = list(MOOD_SCALE.keys())

            # Use radio as a workaround for mood selection inside form
            selected_mood = st.radio(
                "Select your mood",
                mood_emojis,
                format_func=lambda x: f"{x} {MOOD_SCALE[x]['label']}",
                horizontal=True,
                label_visibility="collapsed",
                index=1,  # Default to "Good"
            )

            st.markdown("---")

            # Gratitude Prompts
            st.markdown("**🙏 What are you grateful for today?**")
            g1 = st.text_input("1.", placeholder="Something that made you smile...", key="grat_1")
            g2 = st.text_input("2.", placeholder="A person you appreciate...", key="grat_2")
            g3 = st.text_input("3.", placeholder="Something you're looking forward to...", key="grat_3")

            st.markdown("---")

            # Emotion Tags
            st.markdown("**🏷️ How would you describe your emotions?**")
            selected_tags = st.multiselect(
                "Select emotion tags",
                EMOTION_TAGS,
                label_visibility="collapsed",
                max_selections=5,
            )

            st.markdown("---")

            # Free-text Reflection
            st.markdown("**📖 Daily Reflection**")
            journal_text = st.text_area(
                "Write about your day...",
                placeholder="How was your day? What happened? How did you feel about it?",
                height=150,
                label_visibility="collapsed",
            )

            # Submit
            submitted = st.form_submit_button("💾 Save Journal Entry", width="stretch", type="primary")

            if submitted:
                if selected_mood:
                    result = journal_service.save_entry(
                        user_id=user_id,
                        mood_emoji=selected_mood,
                        journal_text=journal_text,
                        gratitude_items=[g1, g2, g3],
                        tags=selected_tags,
                    )
                    if result.get("success"):
                        st.session_state["journal_editing"] = False
                        st.success("✅ Journal entry saved! Keep reflecting — you're building a great habit.")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Failed to save entry. Please try again.")
                else:
                    st.warning("Please select a mood before saving.")

    # ── Recent Entries Timeline ────────────────────────
    st.markdown("---")
    st.markdown("### 📅 Recent Entries")

    entries = journal_service.get_entries(user_id, days=14)

    if not entries:
        st.info("No journal entries yet. Start writing above to begin your wellness journey! 📝")
    else:
        for entry in entries[:10]:  # Show last 10
            date_str = entry.get("date", "")
            try:
                dt = datetime.fromisoformat(entry.get("timestamp", date_str))
                display_date = dt.strftime("%A, %B %d")
            except Exception:
                display_date = date_str

            mood_emoji = entry.get("mood_emoji", "😐")
            mood_label = entry.get("mood_label", "Okay")
            text_preview = entry.get("journal_text", "")[:120]
            tags = entry.get("tags", [])
            gratitude = entry.get("gratitude", [])

            # Tag pills HTML
            tags_html = ""
            if tags:
                tags_html = " ".join(
                    f'<span style="background:rgba(108,99,255,0.15); color:rgba(255,255,255,0.7); '
                    f'padding:2px 10px; border-radius:20px; font-size:12px; margin-right:4px;">{html.escape(t)}</span>'
                    for t in tags[:3]
                )

            with st.expander(f"{mood_emoji} {display_date} — {mood_label}", expanded=False):
                if text_preview:
                    st.markdown(f"*{html.escape(entry.get('journal_text', ''))}*")
                if gratitude:
                    st.markdown("**🙏 Gratitude:**")
                    for g in gratitude:
                        st.markdown(f"- {html.escape(g)}")
                if tags:
                    st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)
