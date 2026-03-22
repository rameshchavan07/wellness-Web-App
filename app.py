"""
DayScore — Smart Wellness Tracking App
Main application entry point.
Built with Streamlit + Firebase + Google Fit.
"""
#streamlit run app.py
import streamlit as st

from config.settings import AppConfig
from auth.auth_service import AuthService
from auth.google_oauth import get_google_auth_url, handle_google_callback
from utils.ui_components import inject_custom_css
from services.google_fit_service import GoogleFitService

# ── Page Configuration ─────────────────────────────────
st.set_page_config(
    page_title="DayScore — Smart Wellness Tracker",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom CSS
inject_custom_css()

# ── Authentication Gate ────────────────────────────────
def render_login_page():
    """Render the login / sign-up page."""
    auth_service = AuthService()

    # Handle Google Sign-In / Fit Setup callback all at once
    google_callback_res = handle_google_callback()
    if google_callback_res:
        if google_callback_res.get("success"):
            sign_in_res = auth_service.sign_in_with_google(google_callback_res["user_info"])
            if sign_in_res["success"]:
                st.session_state["authenticated"] = True
                st.session_state["user"] = sign_in_res["user"]
                st.session_state["token"] = sign_in_res.get("token", "")
                
                # Store the Google Fit payload!
                if "raw_tokens" in google_callback_res:
                    st.session_state["google_fit_credentials"] = google_callback_res["raw_tokens"]
                    st.session_state["google_fit_connected"] = True
                    
                st.success("✅ Connected to Google & DayScore!")
                st.rerun()
            else:
                st.error(sign_in_res["error"])
        else:
            st.error(google_callback_res.get("error", "Google auth failed."))
    # Centered branding
    st.markdown("""
    <div style="text-align:center; padding:60px 20px 40px 20px;">
        <div style="font-size:72px; margin-bottom:8px;">💙</div>
        <h1 style="font-size:48px; font-weight:800; margin:0;
            background: linear-gradient(90deg, #6C63FF, #4ECDC4);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            DayScore
        </h1>
        <p style="color:rgba(255,255,255,0.5); font-size:18px; margin-top:8px;">
            Your Smart Wellness Companion
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Login / Signup tabs
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        auth_tab = st.radio(
            "Account",
            ["Sign In", "Create Account"],
            horizontal=True,
            label_visibility="collapsed",
        )

        if auth_tab == "Sign In":
            with st.form("login_form"):
                st.markdown("### 👋 Welcome Back")
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("🚀 Sign In", use_container_width=True)

                if submitted:
                    if email and password:
                        result = auth_service.sign_in(email, password)
                        if result["success"]:
                            st.session_state["authenticated"] = True
                            st.session_state["user"] = result["user"]
                            st.session_state["token"] = result.get("token", "")
                            st.success("✅ Welcome back!")
                            st.rerun()
                        else:
                            st.error(result["error"])
                    else:
                        st.warning("Please enter email and password.")

        else:
            with st.form("signup_form"):
                st.markdown("### ✨ Create Your Account")
                name = st.text_input("Full Name", placeholder="John Doe")
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="Min 6 characters")
                confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("🎉 Create Account", use_container_width=True)

                if submitted:
                    if not name or not email or not password:
                        st.warning("Please fill in all fields.")
                    elif password != confirm:
                        st.error("Passwords do not match.")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        result = auth_service.sign_up(email, password, name)
                        if result["success"]:
                            st.session_state["authenticated"] = True
                            st.session_state["user"] = result["user"]
                            st.session_state["token"] = result.get("token", "")
                            st.success("🎉 Account created successfully!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(result["error"])

        # Alternative Sign-in Methods
        st.markdown("---")
        
        # Google Sign-In
        google_url = get_google_auth_url()
        if google_url:
            st.markdown(f"""
            <a href="{google_url}" target="_self" style="text-decoration:none;">
                <div style="background:white; color:#757575; border-radius:12px; padding:10px; text-align:center; font-weight:600; margin-bottom:12px; display:flex; align-items:center; justify-content:center; gap:10px; transition:all 0.3s ease;">
                    <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" width="18" height="18" />
                    Continue with Google
                </div>
            </a>
            """, unsafe_allow_html=True)

        st.markdown(
            '<div style="text-align:center; color:rgba(255,255,255,0.4); font-size:14px; margin-bottom:12px;">'
            'or</div>',
            unsafe_allow_html=True,
        )
        if st.button("🎮 Try Demo Mode", use_container_width=True):
            demo_result = auth_service._demo_sign_in("demo@dayscore.app")
            st.session_state["authenticated"] = True
            st.session_state["user"] = demo_result["user"]
            st.session_state["token"] = demo_result["token"]
            st.rerun()

    # Footer
    st.markdown("""
    <div style="text-align:center; margin-top:60px; color:rgba(255,255,255,0.2); font-size:12px;">
        DayScore v1.0.0 — Built with Streamlit + Firebase + Google Fit
    </div>
    """, unsafe_allow_html=True)


# ── Main App (authenticated) ──────────────────────────
def render_main_app():
    """Render the main application with sidebar navigation."""
    user = st.session_state.get("user", {})
    auth_service = AuthService()

    # ── Sidebar ────────────────────────────────────────
    with st.sidebar:
        # Branding
        st.markdown("""
        <div style="text-align:center; padding:16px 0;">
            <span style="font-size:36px;">💙</span>
            <h2 style="margin:4px 0 0 0; font-size:24px; font-weight:800;
                background: linear-gradient(90deg, #6C63FF, #4ECDC4);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                DayScore
            </h2>
        </div>
        """, unsafe_allow_html=True)

        # User info
        import html
        safe_name = html.escape(user.get('name', 'User'))
        safe_email = html.escape(user.get('email', ''))
        st.markdown(f"""
        <div style="text-align:center; padding:8px; margin-bottom:16px;
            background:rgba(108,99,255,0.1); border-radius:12px;">
            <div style="font-weight:600; color:white;">{safe_name}</div>
            <div style="font-size:12px; color:rgba(255,255,255,0.4);">{safe_email}</div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation — reliable st.button approach
        st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

        NAV_PAGES = [
            ("Dashboard",    "📊"),
            ("Results",      "📈"),
            ("Achievements", "🏆"),
            ("Challenges",   "👥"),
            ("Messages",     "💬"),
            ("Wellness",     "🧘"),
            ("Settings",     "⚙️"),
        ]

        if "selected_page" not in st.session_state:
            st.session_state.selected_page = "Dashboard"

        for page_name, icon in NAV_PAGES:
            is_active = st.session_state.selected_page == page_name
            btn_type = "primary" if is_active else "secondary"
            
            if st.button(f"{icon}  {page_name}", key=f"nav_{page_name}", use_container_width=True, type=btn_type):
                st.session_state.selected_page = page_name
                st.rerun()

        selected = st.session_state.selected_page

        st.markdown("---")
        if st.button("🚪 Sign Out", use_container_width=True):
            auth_service.sign_out()
            st.rerun()

        # Google Fit status
        fit_status = "🟢 Connected" if st.session_state.get("google_fit_connected") else "🔴 Not Connected"
        st.markdown(f"""
        <div style="text-align:center; margin-top:8px;">
            <span style="font-size:12px; color:rgba(255,255,255,0.3);">
                Google Fit: {fit_status}
            </span>
        </div>
        """, unsafe_allow_html=True)

        # Chat toggle button removed from sidebar; it's now a global floating avatar

    # ── Page Router ────────────────────────────────────
    try:
        if selected == "Dashboard":
            from features.dashboard import render_dashboard
            render_dashboard()
        elif selected == "Results":
            from features.results import render_results
            render_results()
        elif selected == "Achievements":
            from features.achievements import render_achievements
            render_achievements()
        elif selected == "Challenges":
            from features.challenges import render_challenges
            render_challenges()
        elif selected == "Messages":
            from features.messages import render_messages
            render_messages()
        elif selected == "Wellness":
            from features.wellness import render_wellness
            render_wellness()
        elif selected == "Settings":
            from features.settings import render_settings
            render_settings()
    except Exception as page_err:
        import traceback
        st.error(f"🚨 Page error: {page_err}")
        st.code(traceback.format_exc())

    # ── Global Floating Chat ───────────────────────────
    try:
        from features.chat.chat_ui import render_floating_chat
        render_floating_chat()
    except Exception as e:
        import traceback
        print("[DayBot ERROR]", traceback.format_exc())


# ── Global Callback Handlers ───────────────────────────
# Note: Google Fit callback is now unified with handle_google_callback() inside render_login_page.

# ── Entry Point ────────────────────────────────────────
def main():
    if st.session_state.get("authenticated"):
        render_main_app()
    else:
        render_login_page()

if __name__ == "__main__":
    main()
