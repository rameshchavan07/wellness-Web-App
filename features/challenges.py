"""
DayScore - Community Challenges Feature
Create / join challenges and view leaderboard.
"""

import streamlit as st
from services.challenge_service import ChallengeService


def render_challenges():
    """Render the Community Challenges page."""
    user = st.session_state.get("user", {})
    user_id = user.get("user_id", "demo_user_001")
    user_name = user.get("name", "Demo User")

    st.markdown("""
    <h1 style="font-size:32px; font-weight:800; color:#FF6B6B;">
        👥 Community Challenges
    </h1>
    <p style="color:rgba(255,255,255,0.5); margin-bottom:24px;">
        Compete with others and stay motivated together!
    </p>
    """, unsafe_allow_html=True)

    challenge_service = ChallengeService()

    tab1, tab2, tab3 = st.tabs(["🏆 Active Challenges", "➕ Create Challenge", "📊 Leaderboard"])

    # ── Active Challenges ──────────────────────────────
    with tab1:
        challenges = challenge_service.get_active_challenges()

        if not challenges:
            st.info("No active challenges yet. Create one to get started!")
        else:
            for ch in challenges:
                participant_count = len(ch.get("participants", []))
                is_joined = user_id in ch.get("participants", [])

                st.markdown(f"""
                <div class="challenge-card">
                    <div style="display:flex; justify-content:space-between; align-items:start;">
                        <div>
                            <h3 style="margin:0; color:white; font-size:18px;">{ch.get('name', '')}</h3>
                            <p style="color:rgba(255,255,255,0.6); margin:4px 0 12px 0; font-size:14px;">
                                {ch.get('description', '')}
                            </p>
                        </div>
                        <div style="background:rgba(255,107,107,0.2); border-radius:8px; padding:8px 12px; text-align:center;">
                            <div style="font-size:18px; font-weight:700; color:#FF6B6B;">{participant_count}</div>
                            <div style="font-size:10px; color:rgba(255,255,255,0.5);">Participants</div>
                        </div>
                    </div>
                    <div style="display:flex; gap:16px; font-size:13px; color:rgba(255,255,255,0.5);">
                        <span>🎯 {ch.get('goal', '')}</span>
                        <span>⏱️ {ch.get('duration_days', 7)} days</span>
                        <span>📏 {ch.get('metric', 'steps').title()}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if not is_joined:
                    if st.button(f"Join Challenge", key=f"join_{ch.get('id', '')}"):
                        success = challenge_service.join_challenge(ch.get("id", ""), user_id)
                        if success:
                            st.success("✅ Successfully joined the challenge!")
                            st.rerun()
                else:
                    st.markdown(
                        '<span style="color:#4ECDC4; font-size:13px;">✅ You\'re participating!</span>',
                        unsafe_allow_html=True,
                    )
                st.markdown("")

    # ── Create Challenge ───────────────────────────────
    with tab2:
        st.markdown("### Create a New Challenge")

        with st.form("create_challenge_form"):
            name = st.text_input("Challenge Name", placeholder="e.g., 10K Steps Week")
            description = st.text_area("Description", placeholder="Describe the challenge...")
            goal = st.text_input("Goal", placeholder="e.g., Walk 10,000 steps daily")

            col1, col2 = st.columns(2)
            with col1:
                metric = st.selectbox("Metric", ["steps", "calories", "sleep", "score"])
            with col2:
                goal_value = st.number_input("Target Value", min_value=1, value=10000)

            duration = st.slider("Duration (days)", 1, 30, 7)

            submitted = st.form_submit_button("🚀 Create Challenge", use_container_width=True)

            if submitted and name:
                challenge_data = {
                    "name": name,
                    "description": description,
                    "goal": goal,
                    "goal_value": goal_value,
                    "metric": metric,
                    "duration_days": duration,
                }
                cid = challenge_service.create_challenge(user_id, challenge_data)
                if cid:
                    st.success(f"🎉 Challenge created successfully!")
                    st.balloons()

    # ── Leaderboard ────────────────────────────────────
    with tab3:
        st.markdown("### 🏅 Global Leaderboard")

        leaderboard = challenge_service.get_leaderboard()

        if not leaderboard:
            st.info("No leaderboard entries yet.")
        else:
            for i, entry in enumerate(leaderboard):
                rank = i + 1
                rank_icons = {1: "🥇", 2: "🥈", 3: "🥉"}
                rank_icon = rank_icons.get(rank, f"#{rank}")
                is_you = entry.get("user_id") == user_id or entry.get("user_name") == "You"

                extra_class = "top-3" if rank <= 3 else ""
                highlight = "border-left: 3px solid #6C63FF;" if is_you else ""

                st.markdown(f"""
                <div class="leaderboard-row {extra_class}" style="{highlight}">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <span style="font-size:24px; min-width:36px;">{rank_icon}</span>
                        <div>
                            <span style="font-weight:600; color:white;">
                                {entry.get('user_name', 'User')}
                                {'(You)' if is_you else ''}
                            </span>
                        </div>
                    </div>
                    <div style="font-size:20px; font-weight:700; color:#6C63FF;">
                        {entry.get('score', 0)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
