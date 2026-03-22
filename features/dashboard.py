"""
DayScore - Dashboard Feature
Main dashboard page with DayScore gauge, metrics, and weekly trends.
"""

import streamlit as st
from datetime import datetime, timedelta
from config.firebase_config import get_firestore_client

from services.scoring_service import ScoringService
from services.google_fit_service import GoogleFitService
from services.streak_service import StreakService
from services.achievement_service import AchievementService
from services.notification_service import NotificationService
from utils.ui_components import (
    render_score_gauge,
    render_metric_card,
    render_weekly_chart,
    render_breakdown_chart,
)
from utils.helpers import (
    get_greeting,
    format_number,
    get_day_labels,
    get_personalized_suggestions,
    generate_weekly_demo_scores,
)


def render_dashboard():
    """Render the main dashboard page."""
    user = st.session_state.get("user", {})
    user_name = user.get("name", "User")
    user_id = user.get("user_id", "demo_user_001")

    # ── Header ─────────────────────────────────────────
    greeting = get_greeting()
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <h1 style="margin:0; font-size:32px; font-weight:800; 
            background: linear-gradient(90deg, #6C63FF, #4ECDC4);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            {greeting}, {user_name}! 👋
        </h1>
        <p style="color: rgba(255,255,255,0.5); margin-top:4px; font-size:15px;">
            {datetime.now().strftime("%A, %B %d, %Y")} • Here's your wellness snapshot
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Interactive Morning Check-in ───────────────────
    if "mood_logged" not in st.session_state:
        st.session_state.mood_logged = False
        
        # Check Firebase to see if the user already logged a mood today
        db = get_firestore_client()
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        if db and user_id != "demo_user_001":
            try:
                doc = db.collection("users").document(user_id).collection("daily_logs").document(today_str).get()
                if doc.exists:
                    data = doc.to_dict()
                    if "mood" in data:
                        st.session_state.mood_logged = data["mood"]
            except Exception:
                pass
        
    if not st.session_state.mood_logged:
        st.markdown("""
        <div class="metric-card" style="margin-bottom:24px; text-align:center; background:rgba(108,99,255,0.15);">
            <h3 style="margin-top:0;">Good morning! How are you feeling today?</h3>
        </div>
        """, unsafe_allow_html=True)
        cols = st.columns(4)
        emojis = [("🤩", "Great"), ("😊", "Good"), ("😐", "Okay"), ("😞", "Rough")]
        for i, (emoji, label) in enumerate(emojis):
            with cols[i]:
                if st.button(f"{emoji} {label}", use_container_width=True, key=f"mood_{i}"):
                    st.session_state.mood_logged = emoji
                    st.rerun()
    else:
        st.markdown(f"""
        <div class="metric-card" style="margin-bottom:24px; display:flex; justify-content:space-between; align-items:center;">
            <div><span style="font-size:24px;">{st.session_state.mood_logged}</span> <strong>Mood Logged</strong></div>
            <div style="color:#4ECDC4; font-weight:600;">+50 Bonus Points!</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Fetch Data ─────────────────────────────────────
    fit_service = GoogleFitService()
    scoring_service = ScoringService()
    streak_service = StreakService()
    achievement_service = AchievementService()
    notification_service = NotificationService()

    google_creds = st.session_state.get("google_fit_credentials", {})
    fitness_data = fit_service.fetch_daily_data(google_creds)

    score_result = scoring_service.calculate_score(fitness_data)
    total_score = score_result["total_score"]
    grade = score_result["grade"]
    breakdown = score_result["breakdown"]
    message = score_result["message"]

    if st.session_state.get("mood_logged"):
        total_score += 50
        
    # Save to Firestore
    db = get_firestore_client()
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    if db and user_id != "demo_user_001":
        log_ref = db.collection("users").document(user_id).collection("daily_logs").document(today_str)
        log_data = {
            "date": today_str,
            "steps": fitness_data.get("steps", 0),
            "calories": fitness_data.get("calories", 0),
            "sleep": fitness_data.get("sleep", 0),
            "heart_rate": fitness_data.get("heart_rate", 0),
            "total_score": total_score,
            "grade": grade,
        }
        if st.session_state.get("mood_logged"):
            log_data["mood"] = st.session_state.mood_logged
            
        try:
            log_ref.set(log_data, merge=True)
        except Exception as e:
            st.error(f"Failed to save to Firebase: {e}")

    # Update streak
    streak = streak_service.update_streak(user_id)
    sleep_streak = streak_service.update_sleep_streak(user_id, fitness_data.get("sleep", 0))

    # Check achievements
    achievement_data = {
        **fitness_data,
        "total_score": total_score,
        "streak": streak,
        "sleep_streak": sleep_streak,
    }
    new_achievements = achievement_service.check_achievements(user_id, achievement_data)

    # Show achievement popups
    for ach in new_achievements:
        st.balloons()
        st.success(f"🎉 Achievement Unlocked: {ach['icon']} **{ach['name']}** — {ach['description']}")

    # Notifications
    notifications = notification_service.get_active_notifications(fitness_data, total_score)
    notification_service.display_notifications(notifications)

    # ── Score Section ──────────────────────────────────
    col1, col2 = st.columns([1, 1])

    with col1:
        st.plotly_chart(
            render_score_gauge(total_score, grade),
            use_container_width=True,
            config={"displayModeBar": False},
        )
        # Motivational message
        st.markdown(f"""
        <div style="text-align:center; padding:8px; 
            background: rgba(108,99,255,0.1); border-radius:12px; margin-top:-8px;">
            <span style="font-size:16px;">{message}</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Streak & quick stats
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <div style="font-size:48px;">🔥</div>
            <div style="font-size:36px; font-weight:800; color:#FFD93D;">{streak}</div>
            <div style="color:rgba(255,255,255,0.6); font-size:14px;">Day Streak</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:8px;">
            <div class="metric-card" style="text-align:center; padding:16px;">
                <div style="font-size:24px; font-weight:700; color:#4ECDC4;">{format_number(fitness_data.get('steps', 0))}</div>
                <div style="color:rgba(255,255,255,0.5); font-size:12px;">🚶 Steps</div>
            </div>
            <div class="metric-card" style="text-align:center; padding:16px;">
                <div style="font-size:24px; font-weight:700; color:#FF6B6B;">{fitness_data.get('sleep', 0)}h</div>
                <div style="color:rgba(255,255,255,0.5); font-size:12px;">😴 Sleep</div>
            </div>
            <div class="metric-card" style="text-align:center; padding:16px;">
                <div style="font-size:24px; font-weight:700; color:#FFD93D;">{format_number(fitness_data.get('calories', 0))}</div>
                <div style="color:rgba(255,255,255,0.5); font-size:12px;">🔥 Calories</div>
            </div>
            <div class="metric-card" style="text-align:center; padding:16px;">
                <div style="font-size:24px; font-weight:700; color:#FF8C42;">{fitness_data.get('heart_rate', 0)}</div>
                <div style="color:rgba(255,255,255,0.5); font-size:12px;">❤️ BPM</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Score Breakdown ────────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Score Breakdown")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.plotly_chart(
            render_breakdown_chart(breakdown),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with col_b:
        render_metric_card("🚶", "Steps", format_number(fitness_data.get("steps", 0)),
                           breakdown["steps"]["score"], "#6C63FF")
        render_metric_card("😴", "Sleep", f'{fitness_data.get("sleep", 0)}h',
                           breakdown["sleep"]["score"], "#4ECDC4")
        render_metric_card("🔥", "Calories", format_number(fitness_data.get("calories", 0)),
                           breakdown["calories"]["score"], "#FFD93D")
        render_metric_card("❤️", "Heart Rate", f'{fitness_data.get("heart_rate", 0)} BPM',
                           breakdown["heart_rate"]["score"], "#FF6B6B")

    # ── Weekly Trend ───────────────────────────────────
    st.markdown("---")
    st.markdown("### 📈 Weekly Trend")

    weekly_scores = [0] * 7
    day_labels = get_day_labels(7)
    
    if db and user_id != "demo_user_001":
        try:
            # Fetch last 7 days from Firestore natively
            logs = db.collection("users").document(user_id).collection("daily_logs").order_by("date", direction="DESCENDING").limit(7).stream()
            log_dict = {doc.to_dict().get("date"): doc.to_dict().get("total_score", 0) for doc in logs}
            
            for i in range(7):
                date_str = (datetime.utcnow() - timedelta(days=6-i)).strftime("%Y-%m-%d")
                weekly_scores[i] = log_dict.get(date_str, 0)
        except Exception as e:
            weekly_scores = generate_weekly_demo_scores()
    else:
        weekly_scores = generate_weekly_demo_scores()

    # Replace last day with today's actual score
    weekly_scores[-1] = total_score

    st.plotly_chart(
        render_weekly_chart(weekly_scores, day_labels),
        use_container_width=True,
        config={"displayModeBar": False},
    )

    # ── Personalized Suggestions ───────────────────────
    st.markdown("### 💡 Personalized Suggestions")
    suggestions = get_personalized_suggestions(breakdown)

    cols = st.columns(len(suggestions))
    for i, sug in enumerate(suggestions):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:32px; margin-bottom:8px;">{sug['icon']}</div>
                <div style="font-weight:600; color:white; margin-bottom:4px;">{sug['title']}</div>
                <div style="color:rgba(255,255,255,0.6); font-size:13px;">{sug['tip']}</div>
            </div>
            """, unsafe_allow_html=True)
