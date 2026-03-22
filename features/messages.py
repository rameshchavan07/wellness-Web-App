"""
DayScore - Direct Messaging Feature
Provides an Inbox UI for user-to-user chatting.
"""
import streamlit as st
import html
from streamlit_autorefresh import st_autorefresh
from services.messaging_service import MessagingService
from config.settings import AppConfig

def render_messages():
    """Render the main Direct Messaging inbox."""
    msg_service = MessagingService()
    current_user = st.session_state.get("user", {})
    current_user_id = current_user.get("user_id", AppConfig.DEMO_USER_ID)
    
    
    # ── Premium UI CSS Injection ──
    st.markdown("""
    <style>
    /* Premium Chat Bubbles styling */
    [data-testid="stChatMessage"] {
        background: rgba(20, 22, 33, 0.6);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 12px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 8px;
        transition: transform 0.2s ease;
    }
    [data-testid="stChatMessage"]:hover {
        transform: translateY(-2px);
    }
    [data-testid="stChatMessageAvatar"] {
        background-color: transparent !important;
        font-size: 24px;
    }
    [data-testid="stCaptionContainer"] {
        opacity: 0.5;
        font-size: 0.75rem;
        margin-top: -4px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h1 style="margin:0; font-size:32px; font-weight:800; 
            background: linear-gradient(90deg, #6C63FF, #4ECDC4);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Messages 💬
        </h1>
        <p style="color: rgba(255,255,255,0.5); margin-top:4px; font-size:15px;">
            Connect with friends, share progress, and stay motivated together.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # ── Sidebar / User List ──────────────────────────────────
    # Create a 2-column layout: Contacts | Active Chat
    col_contacts, col_chat = st.columns([1, 2.5])
    
    users = msg_service.get_users_list(current_user_id)
    
    with col_contacts:
        st.markdown("### 👥 People")
        
        if not users:
            st.info("No other users found yet.")
        else:
            from streamlit_option_menu import option_menu
            user_names = [u["name"] for u in users]
            active_id = st.session_state.get("active_chat_user_id")
            
            default_idx = 0
            for i, u in enumerate(users):
                if u["user_id"] == active_id:
                    default_idx = i
                    break
                    
            selected_name = option_menu(
                menu_title=None,
                options=user_names,
                icons=["person"] * len(users),
                default_index=default_idx,
                styles={
                    "container": {"padding": "0!important", "background-color": "transparent"},
                    "icon": {"color": "#4ECDC4", "font-size": "16px"}, 
                    "nav-link": {"font-size": "14px", "text-align": "left", "margin":"4px 0", "--hover-color": "rgba(108,99,255,0.1)", "border-radius": "8px"},
                    "nav-link-selected": {"background": "linear-gradient(90deg, rgba(108,99,255,0.2), rgba(78,205,196,0.1))", "color": "white", "border-left": "3px solid #6C63FF"},
                }
            )
            
            if selected_name:
                selected_user = next((u for u in users if u["name"] == selected_name), None)
                if selected_user and selected_user["user_id"] != active_id:
                    st.session_state["active_chat_user"] = selected_user
                    st.session_state["active_chat_user_id"] = selected_user["user_id"]
                    st.rerun()

    # ── Main Chat Area ───────────────────────────────────────
    with col_chat:
        active_user = st.session_state.get("active_chat_user")
        
        if not active_user:
            st.markdown("""
            <div style="height: 400px; display:flex; align-items:center; justify-content:center; flex-direction:column; 
                background: linear-gradient(180deg, rgba(108,99,255,0.02) 0%, rgba(78,205,196,0.02) 100%);
                border-radius: 20px; border: 1px dashed rgba(255,255,255,0.1);">
                <div style="font-size: 64px; animation: float 3s ease-in-out infinite;">💬</div>
                <h3 style="margin-top: 16px; color: white;">Your Inbox</h3>
                <p style="color: rgba(255,255,255,0.5);">Select a conversation to start chatting</p>
                <style>
                    @keyframes float {
                        0% { transform: translateY(0px); }
                        50% { transform: translateY(-10px); }
                        100% { transform: translateY(0px); }
                    }
                </style>
            </div>
            """, unsafe_allow_html=True)
            return

        # Chat Header
        st.markdown(f"""
        <div style="display:flex; align-items:center; padding: 12px 20px; background: rgba(0,0,0,0.2); 
            border-radius: 12px; margin-bottom: 16px; border: 1px solid rgba(255,255,255,0.05);">
            <div style="font-size:24px; margin-right: 12px; background: rgba(108,99,255,0.2); 
                height: 40px; width: 40px; display:flex; align-items:center; justify-content:center; border-radius: 50%;">
                👤
            </div>
            <div>
                <h3 style="margin:0; font-size: 18px;">{html.escape(active_user['name'])}</h3>
                <span style="font-size: 12px; color: #4ECDC4;">● Online</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add auto-refresh mechanism (checks every 3 seconds)
        st_autorefresh(interval=3000, key="chat_refresh")
        
        # Chat History Container
        chat_container = st.container(height=500, border=False)
        
        # Load Messages
        messages = msg_service.get_conversation(current_user_id, active_user["user_id"])
        
        with chat_container:
            if not messages:
                st.info("Say hi to start the conversation! ✋")
            else:
                for msg in messages:
                    is_me = msg["sender_id"] == current_user_id
                    avatar = "🧘" if is_me else "👤"
                    
                    # Format timestamp
                    from datetime import datetime
                    time_str = ""
                    try:
                        dt = datetime.fromisoformat(msg.get("timestamp", "").replace("Z", "+00:00"))
                        time_str = dt.strftime("%b %d, %I:%M %p")
                    except Exception:
                        pass
                        
                    with st.chat_message("user" if is_me else "assistant", avatar=avatar):
                        st.write(msg["text"])
                        if time_str:
                            st.caption(time_str)
                        
        # Message Input Box
        new_msg = st.chat_input(f"Message {html.escape(active_user['name'])}...")
        if new_msg:
            # Send message to DB
            success = msg_service.send_message(current_user_id, active_user["user_id"], new_msg)
            if success:
                st.rerun()
            else:
                st.error("Failed to send message.")
