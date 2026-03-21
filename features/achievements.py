"""
DayScore - Achievements Feature
Displays user achievements and achievement catalog.
"""

import streamlit as st
from services.achievement_service import AchievementService


def render_achievements():
    """Render the achievements page."""
    user_id = st.session_state.get("user", {}).get("user_id", "demo_user_001")

    st.markdown("""
    <h1 style="font-size:32px; font-weight:800; color:#FFD93D;">
        🏆 Achievements
    </h1>
    <p style="color:rgba(255,255,255,0.5); margin-bottom:24px;">
        Track your milestones and unlock badges as you improve your health!
    </p>
    """, unsafe_allow_html=True)

    achievement_service = AchievementService()
    unlocked = achievement_service.get_user_achievements(user_id)
    unlocked_ids = {a["id"] for a in unlocked}
    all_achievements = achievement_service.get_all_achievements()

    # Stats
    total = len(all_achievements)
    earned = len(unlocked)
    pct = int((earned / total * 100)) if total > 0 else 0

    st.markdown(f"""
    <div class="score-card" style="margin-bottom:24px;">
        <div style="font-size:48px; font-weight:800;">{earned}/{total}</div>
        <div style="font-size:16px; opacity:0.9;">Achievements Unlocked</div>
        <div style="margin-top:12px;">
            <div class="custom-progress" style="height:8px; background:rgba(255,255,255,0.2);">
                <div class="custom-progress-fill" style="width:{pct}%; background:white;"></div>
            </div>
        </div>
        <div style="font-size:14px; opacity:0.7; margin-top:8px;">{pct}% Complete</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Unlocked Achievements ──────────────────────────
    if unlocked:
        st.markdown("### ✨ Unlocked")
        cols = st.columns(3)
        for i, ach in enumerate(unlocked):
            with cols[i % 3]:
                unlocked_at = ach.get("unlocked_at", "")
                if unlocked_at:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(unlocked_at)
                        date_str = dt.strftime("%b %d, %Y")
                    except Exception:
                        date_str = unlocked_at
                else:
                    date_str = "Recently"

                st.markdown(f"""
                <div class="achievement-badge">
                    <div style="font-size:42px; margin-bottom:8px;">{ach.get('icon', '🏅')}</div>
                    <div style="font-weight:700; color:white; font-size:15px;">{ach.get('name', '')}</div>
                    <div style="color:rgba(255,255,255,0.6); font-size:12px; margin-top:4px;">
                        {ach.get('description', '')}
                    </div>
                    <div style="color:#4ECDC4; font-size:11px; margin-top:8px;">
                        🔓 {date_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Locked Achievements ────────────────────────────
    locked = {k: v for k, v in all_achievements.items() if k not in unlocked_ids}
    if locked:
        st.markdown("### 🔒 Locked")
        cols = st.columns(3)
        for i, (key, ach) in enumerate(locked.items()):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="achievement-locked">
                    <div style="font-size:42px; margin-bottom:8px; filter:grayscale(100%);">{ach.get('icon', '🏅')}</div>
                    <div style="font-weight:600; color:rgba(255,255,255,0.5); font-size:15px;">{ach.get('name', '')}</div>
                    <div style="color:rgba(255,255,255,0.3); font-size:12px; margin-top:4px;">
                        {ach.get('description', '')}
                    </div>
                    <div style="color:rgba(255,255,255,0.2); font-size:11px; margin-top:8px;">🔒 Locked</div>
                </div>
                """, unsafe_allow_html=True)

    # ── Achievement Categories ─────────────────────────
    st.markdown("---")
    st.markdown("### 📂 By Category")

    categories = {}
    for key, ach in all_achievements.items():
        cat = ach.get("category", "general")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({**ach, "unlocked": key in unlocked_ids})

    cat_icons = {"steps": "🚶", "streak": "🔥", "score": "⭐", "sleep": "😴",
                 "calories": "🔥", "general": "🎯"}

    for cat, items in categories.items():
        icon = cat_icons.get(cat, "📌")
        earned_in_cat = sum(1 for i in items if i["unlocked"])
        st.markdown(f"**{icon} {cat.title()}** — {earned_in_cat}/{len(items)} unlocked")
        progress = earned_in_cat / len(items) * 100 if items else 0
        st.progress(progress / 100)
