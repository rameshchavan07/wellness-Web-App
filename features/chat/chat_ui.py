"""
DayScore - Chatbot Widget
Fully native Streamlit implementation — no iframes, no session loss.
Chat button lives in the sidebar; chat panel displays inline on the page.
"""

import streamlit as st


import base64
import os

def render_chat_button_in_sidebar():
    pass  # We removed the sidebar button; the floating avatar will toggle it directly from the main view!


def render_floating_chat():
    """Renders the chat popover panel using the Indian avatar floating button."""

def render_floating_chat():
    """Renders the chat popover panel using the Indian avatar floating button."""

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "bot", "content": "Hi! I'm DayBot 👋 How can I help you today?"}
        ]
    if "chat_personality" not in st.session_state:
        st.session_state.chat_personality = "Friendly"
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False

    # Read the avatar image robustly
    avatar_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "indian_avatar.png"))
    if os.path.exists(avatar_path):
        with open(avatar_path, "rb") as f:
            b64_avatar = base64.b64encode(f.read()).decode()
    else:
        # Fallback empty or some placeholder - shouldn't happen
        b64_avatar = ""

    st.markdown(f"""
    <style>
    /* Float the Avatar Button Container */
    div.st-key-daybot_avatar_btn {{
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        z-index: 999999 !important;
    }}
    
    /* Override the actual button inside the container */
    div.st-key-daybot_avatar_btn button {{
        width: 85px !important;
        height: 85px !important;
        border-radius: 50% !important;
        background-color: #f0f2f6 !important;
        background-image: url("data:image/png;base64,{b64_avatar}") !important;
        background-size: cover !important;
        background-position: center top !important;
        background-repeat: no-repeat !important;
        border: 4px solid #4ECDC4 !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3) !important;
        color: transparent !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
        padding: 0 !important;
        cursor: pointer !important;
    }}
    div.st-key-daybot_avatar_btn button:hover {{
        transform: scale(1.08) !important;
        box-shadow: 0 12px 32px rgba(0,0,0,0.4) !important;
        border-color: #6C63FF !important;
        color: transparent !important;
    }}
    
    /* Hide all inner Streamlit text nodes like <p> */
    div.st-key-daybot_avatar_btn button * {{
        display: none !important;
        color: transparent !important;
    }}

    /* Float the Chat Panel */
    div[data-testid="stVerticalBlock"]:has(#daybot-chat-panel) {{
        position: fixed !important;
        bottom: 115px !important;
        right: 30px !important;
        width: 380px !important;
        height: 520px !important;
        background: linear-gradient(160deg, #13162a, #0f111c) !important;
        border: 1px solid rgba(108,99,255,0.3) !important;
        border-radius: 20px !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5) !important;
        padding: 16px !important;
        z-index: 999998 !important;
        overflow-y: hidden !important;
        display: flex !important;
        flex-direction: column !important;
    }}

    .daybot-header {{
        background: linear-gradient(135deg, #6C63FF, #4ECDC4);
        padding: 12px 16px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }}
    </style>
    """, unsafe_allow_html=True)

    # ── Floating Avatar Button ────────────────────────
    if st.button("Avatar", key="daybot_avatar_btn"):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun()

    # ── Floating Chat Panel ───────────────────────────
    if st.session_state.chat_open:
        chat_wrapper = st.container()
        with chat_wrapper:
            st.markdown('<div id="daybot-chat-panel"></div>', unsafe_allow_html=True)
            
            # ── Chat Header ───────────────────────────────────
            st.markdown("""
            <div class="daybot-header">
                <div style="width:40px;height:40px;border-radius:50%;background:rgba(255,255,255,0.2);
                    display:flex;align-items:center;justify-content:center;font-size:22px;">🤖</div>
                <div>
                    <div style="font-weight:700;color:white;font-size:16px;">DayBot</div>
                    <div style="font-size:11px;color:rgba(255,255,255,0.8);display:flex;align-items:center;gap:5px;">
                        <span style="width:8px;height:8px;border-radius:50%;background:#6effc7;display:inline-block;"></span>
                        Online · Wellness AI
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Personality Selector ──────────────────────────
            pers_options = ["Friendly", "Professional", "Rude"]
            current_idx = pers_options.index(st.session_state.chat_personality) \
                if st.session_state.chat_personality in pers_options else 0

            selected_pers = st.radio(
                "Personality",
                options=["😊 Friendly", "🧑‍💼 Professional", "😈 Rude"],
                horizontal=True,
                label_visibility="collapsed",
                key="chat_personality_radio",
                index=current_idx,
            )
            st.session_state.chat_personality = selected_pers.split(" ", 1)[1]

            st.markdown("<hr style='margin: 8px 0; border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

            # ── Message History ───────────────────────────────
            chat_box = st.container(height=260)
            with chat_box:
                for msg in st.session_state.chat_history:
                    role = "user" if msg["role"] == "user" else "assistant"
                    with st.chat_message(role, avatar="🤖" if role == "assistant" else "👤"):
                        st.write(msg["content"])

            # ── Input Callback logic ──────────────────────────
            def submit_chat():
                user_msg = st.session_state.daybot_input_temp
                if user_msg:
                    st.session_state.chat_history.append({"role": "user", "content": user_msg})
                    # Attempt backend generation
                    try:
                        from features.chat.chat_logic import generate_response
                        reply = generate_response(
                            st.session_state.chat_history,
                            st.session_state.chat_personality
                        )
                    except Exception as e:
                        reply = f"Oops! Something went wrong. ({e})"
                    st.session_state.chat_history.append({"role": "bot", "content": reply})
                    # Clear the input
                    st.session_state.daybot_input_temp = ""

            st.text_input(
                "Type a message...",
                key="daybot_input_temp",
                on_change=submit_chat,
                placeholder="Ask DayBot anything...",
                label_visibility="collapsed"
            )
