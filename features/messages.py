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
        st.markdown("<hr style='margin: 8px 0; opacity: 0.2;'>", unsafe_allow_html=True)
        
        if not users:
            st.info("No other users found yet.")
        else:
            for u in users:
                is_selected = st.session_state.get("active_chat_user_id") == u["user_id"]
                btn_type = "primary" if is_selected else "secondary"
                
                # Render a user button
                if st.button(f"👤 {u['name']}", key=f"chat_btn_{u['user_id']}", use_container_width=True, type=btn_type):
                    st.session_state["active_chat_user"] = u
                    st.session_state["active_chat_user_id"] = u["user_id"]
                    st.rerun()

    # ── Main Chat Area ───────────────────────────────────────
    with col_chat:
        active_user = st.session_state.get("active_chat_user")
        
        if not active_user:
            st.markdown("""
            <div style="height: 400px; display:flex; align-items:center; justify-content:center; flex-direction:column; border-left: 1px solid rgba(255,255,255,0.1);">
                <span style="font-size: 48px; opacity:0.5;">👋</span>
                <p style="color: rgba(255,255,255,0.5); margin-top: 16px;">Select a person to start chatting</p>
            </div>
            """, unsafe_allow_html=True)
            return

        # Chat Header
        st.markdown(f"### 💬 Chat with {html.escape(active_user['name'])}")
        
        # Add auto-refresh mechanism (checks every 3 seconds)
        st_autorefresh(interval=3000, key="chat_refresh")
            
        st.markdown("<hr style='margin: 8px 0; opacity: 0.2;'>", unsafe_allow_html=True)
        
        # Chat History Container
        chat_container = st.container(height=500)
        
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
