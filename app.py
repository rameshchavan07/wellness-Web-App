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
from utils.session_manager import SessionManager

# ── Global Initializations ────────────────────────────
SessionManager.initialize()
sm = SessionManager()


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
                sm.is_authenticated = True
                sm.user = sign_in_res["user"]
                sm.token = sign_in_res.get("token", "")
                
                # Restore existing Google Fit payload from DB if available
                if "google_fit_credentials" in sign_in_res["user"]:
                    sm.google_fit_credentials = sign_in_res["user"]["google_fit_credentials"]
                    sm.google_fit_connected = True

                # Store the new Google Fit payload from callback ONLY if the
                # token was granted fitness scopes (i.e. came from the Fit
                # authorization flow, not the basic sign-in flow).
                if "raw_tokens" in google_callback_res:
                    tokens = google_callback_res["raw_tokens"]
                    granted_scopes = tokens.get("scopes", [])
                    has_fitness_scope = any("fitness" in s for s in granted_scopes)
                    if has_fitness_scope:
                        sm.google_fit_credentials = tokens
                        sm.google_fit_connected = True
                        auth_service.update_user_profile(sign_in_res["user"]["user_id"], {"google_fit_credentials": tokens})
                    
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
                submitted = st.form_submit_button("🚀 Sign In", width="stretch")

                if submitted:
                    if email and password:
                        result = auth_service.sign_in(email, password)
                        if result["success"]:
                            sm.is_authenticated = True
                            sm.user = result["user"]
                            sm.token = result.get("token", "")

                            # Restore Google Fit payload from DB if available
                            if "google_fit_credentials" in result["user"]:
                                sm.google_fit_credentials = result["user"]["google_fit_credentials"]
                                sm.google_fit_connected = True
                                
                            st.success("✅ Welcome back!")
                            st.rerun()
                        else:
                            st.error(result["error"])
                    else:
                        st.warning("Please enter email and password.")

        else:
            with st.form("signup_form"):
                st.markdown("### ✨ Create Your Account")
                
                # Role selection
                is_counselor = st.checkbox("🩺 I am a Counselor/Doctor", value=False)
                
                name = st.text_input("Full Name", placeholder="John Doe")
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password", placeholder="Min 6 characters")
                confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                
                specialty = ""
                clinic = ""
                if is_counselor:
                    st.markdown("##### Professional Details")
                    specialty = st.text_input("Specialty", placeholder="e.g. Clinical Psychologist, Therapist")
                    clinic = st.text_input("Hospital / Clinic Name", placeholder="e.g. Wellness Center")
                
                submitted = st.form_submit_button("🎉 Create Account", width="stretch")

                if submitted:
                    if not name or not email or not password:
                        st.warning("Please fill in all required fields.")
                    elif is_counselor and not specialty:
                        st.warning("Counselors must provide a specialty.")
                    elif password != confirm:
                        st.error("Passwords do not match.")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        result = auth_service.sign_up(
                            email=email, 
                            password=password, 
                            display_name=name, 
                            is_counselor=is_counselor,
                            specialty=specialty,
                            clinic=clinic
                        )
                        if result["success"]:
                            sm.is_authenticated = True
                            sm.user = result["user"]
                            sm.token = result.get("token", "")
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
        if st.button("🎮 Try Demo Mode", width="stretch"):
            demo_result = auth_service._demo_sign_in("demo@dayscore.app")
            sm.is_authenticated = True
            sm.user = demo_result["user"]
            sm.token = demo_result["token"]
            st.rerun()
            
        if st.button("🩺 Try Counselor Demo", width="stretch"):
            demo_result = auth_service._demo_sign_in("dr.sharma@dayscore.app")
            sm.is_authenticated = True
            sm.user = demo_result["user"]
            sm.token = demo_result["token"]
            st.rerun()

    # Footer
    st.markdown("""
    <div style="text-align:center; margin-top:60px; color:rgba(255,255,255,0.2); font-size:12px;">
        DayScore v1.0.0 — Built with Streamlit + Firebase + Google Fit
    </div>
    """, unsafe_allow_html=True)


# ── Page Callables (Optimized Lazy Loading) ────────────
def page_dashboard():
    from features.dashboard import render_dashboard
    render_dashboard()

def page_results():
    from features.results import render_results
    render_results()

def page_achievements():
    from features.achievements import render_achievements
    render_achievements()

def page_challenges():
    from features.challenges import render_challenges
    render_challenges()

def page_journal():
    from features.journal import render_journal
    render_journal()

def page_mental_health():
    from features.mental_health import render_mental_health
    render_mental_health()

def page_counselor():
    from features.counselor import render_counselor
    render_counselor()

def page_messages():
    from features.messages import render_messages
    render_messages()

def page_wellness():
    from features.wellness import render_wellness
    render_wellness()

def page_settings():
    from features.settings import render_settings
    render_settings()

def page_counselor_dashboard():
    from features.counselor_dashboard import render_counselor_dashboard
    render_counselor_dashboard()

# Define Navigation Pages globally to avoid re-instantiation
PATIENT_PAGES = [
    st.Page(page_dashboard, title="Dashboard", icon="📊", default=True),
    st.Page(page_results, title="Results", icon="📈"),
    st.Page(page_achievements, title="Achievements", icon="🏆"),
    st.Page(page_challenges, title="Challenges", icon="👥"),
    st.Page(page_journal, title="Journal", icon="📓"),
    st.Page(page_mental_health, title="Mental Health", icon="🧠"),
    st.Page(page_counselor, title="Counselor", icon="🩺"),
    st.Page(page_messages, title="Messages", icon="💬"),
    st.Page(page_wellness, title="Wellness", icon="🧘"),
    st.Page(page_settings, title="Settings", icon="⚙️"),
]

COUNSELOR_PAGES = [
    st.Page(page_counselor_dashboard, title="My Patients", icon="👥", default=True),
    st.Page(page_settings, title="Settings", icon="⚙️"),
]

# ── Sidebar Components ─────────────────────────────────
def render_sidebar_header(user):
    """Render common sidebar elements once."""
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

def render_sidebar_footer():
    """Render logout and status at bottom of sidebar."""
    auth_service = AuthService()
    with st.sidebar:
        st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🚪 Sign Out", width="stretch"):
            auth_service.sign_out()
            st.rerun()

        # Google Fit status
        fit_status = "🟢 Connected" if sm.google_fit_connected else "🔴 Not Connected"
        st.markdown(f"""
        <div style="text-align:center; margin-top:8px;">
            <span style="font-size:12px; color:rgba(255,255,255,0.3);">
                Google Fit: {fit_status}
            </span>
        </div>
        """, unsafe_allow_html=True)

# ── Main App (authenticated) ──────────────────────────
def render_main_app():
    """Render the main application with optimized st.navigation."""
    user = sm.user
    
    # Instantiate navigation once per script run
    is_counselor = user.get("role") == "counselor"
    pages_to_use = COUNSELOR_PAGES if is_counselor else PATIENT_PAGES
    pg = st.navigation(pages_to_use)

    # Render Header (Above Nav)
    render_sidebar_header(user)

    # Run Current Page
    try:
        pg.run()
    except Exception as page_err:
        import traceback
        tb = traceback.format_exc()
        print("Page Error:", tb)  # Always visible in Streamlit Cloud logs
        st.error(f"🚨 Page error: {page_err}")
        if AppConfig.DEBUG:
            st.code(tb)

    # Render Footer (Below Nav)
    render_sidebar_footer()

    # floating chat
    try:
        from features.chat.chat_ui import render_floating_chat
        render_floating_chat()
    except Exception as e:
        pass
# ── Global Callback Handlers ───────────────────────────
# Note: Google Fit callback is now unified with handle_google_callback() inside render_login_page.

# ── Entry Point ────────────────────────────────────────
def main():
    if sm.is_authenticated:
        render_main_app()
    else:
        render_login_page()

if __name__ == "__main__":
    main()
