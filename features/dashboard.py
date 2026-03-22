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
from config.settings import AppConfig
import html

def render_dashboard():
    """Render the main dashboard page."""
    user = st.session_state.get("user", {})
    user_name = html.escape(user.get("name", "User"))
    user_id = user.get("user_id", AppConfig.DEMO_USER_ID)

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
        if db and user_id != AppConfig.DEMO_USER_ID:
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
        
    # Save historical snapshot to Firestore
    if user_id != AppConfig.DEMO_USER_ID:
        # Save mood if configured
        if st.session_state.get("mood_logged"):
            db = get_firestore_client()
            if db:
                try:
                    today_str = datetime.utcnow().strftime("%Y-%m-%d")
                    db.collection("users").document(user_id).collection("daily_logs").document(today_str).set(
                        {"mood": st.session_state.mood_logged, "date": today_str}, merge=True
                    )
                except Exception:
                    pass
        
        # Trigger permanent daily score background sync
        # Uses st.session_state variables so we don't block the UI rendering if it's slightly slow.
        if google_creds:
            fit_service.sync_daily_data_to_firestore(user_id, google_creds)

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

    # ── AI Score Forecast ──────────────────────────────
    from services.prediction_service import PredictionService
    pred_service = PredictionService()
    prediction = pred_service.predict_tomorrow(user_id)
    
    if prediction.get("success"):
        st.markdown(f"""
        <div class="metric-card" style="margin-top:16px; background: linear-gradient(135deg, rgba(108,99,255,0.1), rgba(78,205,196,0.1)); border-left: 4px solid #4ECDC4;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h3 style="margin:0; font-size:18px;">🤖 Tomorrow's AI Forecast</h3>
                    <p style="margin:4px 0 0 0; color:rgba(255,255,255,0.7); font-size:14px;">{prediction['message']}</p>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:32px; font-weight:800; color:white;">{prediction['predicted_score']}</span>
                    <span style="color:rgba(255,255,255,0.5); font-size:14px;">/100</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Social Share ───────────────────────────────────
    st.markdown("---")
    share_cols = st.columns([3, 1])
    with share_cols[0]:
        st.markdown(f"### 📣 Share Your Score")
        st.markdown("Let your friends know how you are doing today!")
        share_text = f"🔥 I just scored {total_score}/100 on my DayScore today! ({fitness_data.get('steps', 0)} steps and {fitness_data.get('sleep', 0)}h of sleep). Check out your own score at dayscore.app!"
        st.code(share_text, language="markdown")
    with share_cols[1]:
        st.markdown("<br>", unsafe_allow_html=True)
        # Using a mailto link or web share API workaround
        twitter_url = f"https://twitter.com/intent/tweet?text={share_text.replace(' ', '%20').replace('/', '%2F').replace('(', '%28').replace(')', '%29')}"
        st.markdown(f"""
        <a href="{twitter_url}" target="_blank" style="text-decoration:none;">
            <div style="background:#1DA1F2; color:white; border-radius:12px; padding:12px; text-align:center; font-weight:600; margin-bottom:12px; transition:all 0.3s ease;">
                🐦 Share to Twitter
            </div>
        </a>
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
    
    if db and user_id != AppConfig.DEMO_USER_ID:
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
