"""
DayScore - Counselor Dashboard
Dashboard for counselors to view their patients and upcoming meetings.
"""

import streamlit as st
import html
from config.settings import AppConfig
from services.counselor_service import CounselorService

def render_counselor_dashboard():
    """Render the dashboard specifically for a logged-in counselor."""
    user = st.session_state.get("user", {})
    counselor_id = user.get("counselor_id")
    
    if not counselor_id:
        st.error("Access Denied: You do not have counselor privileges.")
        return

    counselor_service = CounselorService()
    
    # ── Header ─────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-bottom: 24px;">
        <h1 style="margin:0; font-size:32px; font-weight:800;
            background: linear-gradient(90deg, #FF6B6B, #FFD93D);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🩺 Welcome, {html.escape(user.get('name', 'Counselor'))}
        </h1>
        <p style="color: rgba(255,255,255,0.5); margin-top:4px; font-size:15px;">
            Here are your upcoming appointments and patient requests.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📅 Overview", "👥 My Patients"])
    
    with tab1:
        # ── Upcoming Sessions ──────────────────────────────
        st.markdown("### Upcoming Patient Sessions")
        bookings = counselor_service.get_counselor_bookings(counselor_id)
        
        if not bookings:
            st.info("You have no upcoming sessions booked yet.")
        else:
            for booking in bookings:
                session_type_icon = "🎥" if booking.get("session_type") == "video" else "💬"
                status_color = "#4ECDC4" if booking.get("status") == "confirmed" else "#FFD93D"
                
                # Since we don't have full patient names always populated in demo mode easily,
                # we'll display the user_id or generic patient. In a full system, we'd fetch the patient profile.
                patient_name = booking.get("patient_name", "Patient")
                if "patient_name" not in booking:
                    # Fallback mapping
                    patient_name = "Demo User" if booking.get("user_id") == "demo_12345" else f"Patient ({booking.get('user_id', '')[:5]}...)"

                st.markdown(f"""
                <div class="metric-card" style="margin-bottom:12px; border-left: 4px solid {status_color};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="display:flex; align-items:center; gap:12px;">
                            <div style="font-size:36px;">👤</div>
                            <div>
                                <div style="font-size:16px; font-weight:700; color:white;">
                                    {patient_name}
                                </div>
                                <div style="color:rgba(255,255,255,0.5); font-size:13px;">
                                    Session Type: {booking.get('session_type', 'unknown').title()}
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
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    meet_link = booking.get("meet_link", "")
                    if meet_link and booking.get("session_type") == "video":
                        st.link_button(
                            "🎥 Open Meeting",
                            meet_link,
                            width="stretch",
                            type="primary",
                        )
                    elif booking.get("session_type") == "chat":
                        st.button("💬 Start Chat", key=f"counselor_chat_{booking.get('id', '')}", width="stretch")
                
                st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1); margin: 12px 0;' />", unsafe_allow_html=True)
        
        # ── Quick Tools ────────────────────────────────────
        st.markdown("### 🛠️ Quick Tools")
        tcol1, tcol2, tcol3 = st.columns(3)
        with tcol1:
            st.markdown("""
            <div class="stat-box" style="text-align:center;">
                <h3>📝</h3>
                <p>Write Clinical Notes</p>
            </div>
            """, unsafe_allow_html=True)
        with tcol2:
            st.markdown("""
            <div class="stat-box" style="text-align:center;">
                <h3>📊</h3>
                <p>Review Patient Moods</p>
            </div>
            """, unsafe_allow_html=True)
        with tcol3:
            st.markdown("""
            <div class="stat-box" style="text-align:center;">
                <h3>⚙️</h3>
                <p>Availability Settings</p>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 👥 My Patients")
        
        # Extract unique patients from bookings
        bookings = counselor_service.get_counselor_bookings(counselor_id)
        unique_patients = {}
        for b in bookings:
            uid = b.get("user_id")
            if uid and uid not in unique_patients:
                p_name = b.get("patient_name", "Patient")
                if "patient_name" not in b:
                    p_name = "Demo User" if uid == "demo_12345" else f"Patient ({uid[:5]}...)"
                unique_patients[uid] = {
                    "name": p_name,
                    "last_session": b.get("session_date"),
                    "session_type": b.get("session_type")
                }
        
        if not unique_patients:
            st.info("No patients found in your booking history.")
        else:
            for uid, p_info in unique_patients.items():
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom:12px; border-left: 4px solid #6C63FF;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="display:flex; align-items:center; gap:12px;">
                            <div style="font-size:36px; background: rgba(108, 99, 255, 0.2); border-radius: 50%; padding: 8px;">👤</div>
                            <div>
                                <div style="font-size:18px; font-weight:700; color:white;">
                                    {p_info['name']}
                                </div>
                                <div style="color:rgba(255,255,255,0.5); font-size:13px; margin-top:4px;">
                                    ID: {uid}
                                </div>
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <div style="color:#4ECDC4; font-weight:600; font-size:14px;">
                                Last Session: {p_info['last_session']}
                            </div>
                            <div style="color:rgba(255,255,255,0.5); font-size:12px; margin-top:4px;">
                                Preferred: {p_info['session_type'].title()}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.button("📄 View Records", key=f"view_records_{uid}", width="stretch", help="View patient health records and notes")

