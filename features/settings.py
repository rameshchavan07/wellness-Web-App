"""
DayScore - Settings Feature
User profile settings, Google Fit connection, and app preferences.
"""

import streamlit as st
from services.google_fit_service import GoogleFitService
from auth.auth_service import AuthService
from utils.session_manager import SessionManager

sm = SessionManager()


def render_settings():
    """Render the Settings page."""
    user = sm.user

    st.markdown("""
    <h1 style="font-size:32px; font-weight:800; color:#FFD93D;">
        ⚙️ Settings
    </h1>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🔗 Connections", "🎨 Preferences"])

    with tab1:
        _render_profile(user)

    with tab2:
        _render_connections()

    with tab3:
        _render_preferences()


def _render_profile(user: dict):
    """User profile settings."""
    st.markdown("### 👤 Your Profile")

    col1, col2 = st.columns([1, 2])

    with col1:
        photo = user.get("profile_photo", "")
        if photo:
            st.image(photo, width=120)
        else:
            st.markdown("""
            <div style="width:120px; height:120px; border-radius:50%;
                background: linear-gradient(135deg, #6C63FF, #4ECDC4);
                display:flex; align-items:center; justify-content:center;
                font-size:48px; color:white; font-weight:700;">
                {}
            </div>
            """.format(user.get("name", "U")[0].upper()), unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:24px; font-weight:700; color:white;">
                {user.get('name', 'User')}
            </div>
            <div style="color:rgba(255,255,255,0.5); font-size:14px; margin-top:4px;">
                {user.get('email', '')}
            </div>
            <div style="color:#4ECDC4; font-size:13px; margin-top:8px;">
                🆔 {user.get('user_id', 'N/A')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Edit profile
    st.markdown("---")
    with st.form("edit_profile"):
        new_name = st.text_input("Display Name", value=user.get("name", ""))
        submitted = st.form_submit_button("💾 Update Profile", width="stretch")

        if submitted and new_name:
            auth = AuthService()
            success = auth.update_user_profile(user.get("user_id", ""), {"name": new_name})
            if success:
                user["name"] = new_name
                sm.user = user
                st.success("✅ Profile updated!")
            else:
                user["name"] = new_name
                sm.user = user
                st.success("✅ Profile updated (local)!")


def _render_connections():
    """API connections management."""
    st.markdown("### 🔗 Connected Services")

    # Google Fit
    fit_connected = sm.google_fit_connected

    st.markdown(f"""
    <div class="metric-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-size:18px; font-weight:600; color:white;">
                    Google Fit
                </div>
                <div style="color:rgba(255,255,255,0.5); font-size:13px;">
                    Sync steps, sleep, calories, and heart rate
                </div>
            </div>
            <div style="color:{'#4ECDC4' if fit_connected else '#FF6B6B'}; font-weight:600;">
                {'✅ Connected' if fit_connected else '❌ Not Connected'}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not fit_connected:
        fit_service = GoogleFitService()
        user_id = sm.user.get("user_id", "demo")
        auth_url = fit_service.get_auth_url(user_id)
        if auth_url:
            st.markdown(f"[🔗 Connect Google Fit]({auth_url})")
        else:
            st.info("ℹ️ Configure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env to enable Google Fit.")
    else:
        if st.button("🔌 Disconnect Google Fit"):
            sm.google_fit_connected = False
            sm.google_fit_credentials = {}
            st.success("Disconnected from Google Fit.")
            st.rerun()

    # Demo mode indicator
    st.markdown("---")
    st.markdown("""
    <div class="metric-card" style="border-color: rgba(255,217,61,0.3);">
        <div style="display:flex; align-items:center; gap:12px;">
            <span style="font-size:24px;">🎮</span>
            <div>
                <div style="font-weight:600; color:#FFD93D;">Demo Mode</div>
                <div style="color:rgba(255,255,255,0.5); font-size:13px;">
                    Currently using simulated data. Connect Google Fit for real health data.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_preferences():
    """App preferences."""
    st.markdown("### 🎨 Preferences")

    # Theme (display only — Streamlit handles this via config)
    st.markdown("""
    <div class="metric-card">
        <div style="font-weight:600; color:white; margin-bottom:8px;">Theme</div>
        <div style="color:rgba(255,255,255,0.5); font-size:13px;">
            Using dark mode (configured in .streamlit/config.toml)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Notification preferences
    st.markdown("#### 🔔 Notifications")
    col1, col2 = st.columns(2)
    with col1:
        st.toggle("Low score alerts", value=True, key="pref_low_score")
        st.toggle("Walk reminders", value=True, key="pref_walk")
    with col2:
        st.toggle("Water reminders", value=True, key="pref_water")
        st.toggle("Sleep reminders", value=True, key="pref_sleep")

    # Scoring preferences
    st.markdown("#### 📊 Scoring")
    st.markdown("Adjust ideal targets:")
    col1, col2 = st.columns(2)
    with col1:
        st.number_input("Steps goal", value=10000, step=1000, key="pref_steps_goal")
        st.number_input("Calories goal", value=2000, step=100, key="pref_cal_goal")
    with col2:
        st.number_input("Sleep target (hours)", value=7.5, step=0.5, key="pref_sleep_goal")
        st.number_input("Max heart rate", value=100, step=5, key="pref_hr_max")

    # About
    st.markdown("---")
    st.markdown("""
    <div class="metric-card" style="text-align:center;">
        <div style="font-size:32px; margin-bottom:8px;">💙</div>
        <div style="font-weight:700; font-size:18px; color:white;">DayScore v1.0.0</div>
        <div style="color:rgba(255,255,255,0.5); font-size:13px; margin-top:4px;">
            Your daily wellness companion
        </div>
        <div style="color:rgba(255,255,255,0.3); font-size:11px; margin-top:8px;">
            Built with ❤️ using Streamlit + Firebase + Google Fit
        </div>
    </div>
    """, unsafe_allow_html=True)
