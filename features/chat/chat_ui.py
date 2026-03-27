"""
DayScore - Chatbot Widget
Fully native Streamlit implementation — no iframes, no session loss.
Chat button lives in the sidebar; chat panel displays inline on the page.
"""

import streamlit as st


import base64
import os
from utils.session_manager import SessionManager

sm = SessionManager()

def render_chat_button_in_sidebar():
    pass  # We removed the sidebar button; the floating avatar will toggle it directly from the main view!


def render_floating_chat():
    """Renders the chat popover panel using the Indian avatar floating button."""

    if not sm.chat_history:
        sm.chat_history = [
            {"role": "bot", "content": "Hi! I'm DayBot 👋 How can I help you today?"}
        ]
    
    # sm.chat_personality and sm.chat_open are handles by SessionManager defaults/initialization
    # Read the avatar image robustly
    avatar_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "indian_avatar.png"))
    if os.path.exists(avatar_path):
        with open(avatar_path, "rb") as f:
            b64_avatar = base64.b64encode(f.read()).decode()
    else:
        b64_avatar = ""

    # Escape CSS brackets with double braces {{ and }}
    st.markdown(f"""
    <style>
    @keyframes slideUp {{
        from {{ transform: translateY(20px); opacity: 0; }}
        to {{ transform: translateY(0); opacity: 1; }}
    }}
    @keyframes pulseGlow {{
        0% {{ box-shadow: 0 0 5px rgba(108, 99, 255, 0.4); }}
        50% {{ box-shadow: 0 0 15px rgba(108, 99, 255, 0.8); }}
        100% {{ box-shadow: 0 0 5px rgba(108, 99, 255, 0.4); }}
    }}

    /* 1. Floating Avatar Button */
    div.st-key-daybot_avatar_btn {{
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        z-index: 999999 !important;
    }}
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
        box-shadow: 0 8px 24px rgba(0,0,0,0.4) !important;
        color: transparent !important;
        transition: transform 0.2s ease, border-color 0.2s ease !important;
        padding: 0 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }}
    div.st-key-daybot_avatar_btn button:hover {{
        transform: scale(1.1) rotate(5deg) !important;
        border-color: #6C63FF !important;
    }}
    div.st-key-daybot_avatar_btn button p {{ display: none !important; }}

    /* 2. Premium Glassmorphic Chat Panel */
    .floating-daybot-panel {{
        position: fixed !important;
        bottom: 130px !important;
        right: 30px !important;
        width: 400px !important;
        height: 580px !important;
        background: rgba(15, 18, 59, 0.85) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 24px !important;
        box-shadow: 0 32px 100px rgba(0,0,0,0.9) !important;
        z-index: 999998 !important;
        padding: 0 !important;
        overflow: hidden !important;
        animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    /* Remove Streamlit inner gaps */
    .floating-daybot-panel > div {{
        padding: 0 !important;
        gap: 0 !important;
    }}

    /* 3. AI-Glow Header */
    .daybot-premium-header {{
        background: linear-gradient(135deg, #6C63FF 0%, #3B82F6 100%);
        padding: 24px 20px;
        display: flex;
        align-items: center;
        gap: 14px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
    .ai-icon-glow {{
        width: 44px;
        height: 44px;
        background: rgba(255,255,255,0.15);
        border-radius: 12px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 26px;
        animation: pulseGlow 3s infinite ease-in-out;
    }}

    /* 4. Chat Bubbles Upgrade */
    .chat-bubble-user {{
        background: linear-gradient(135deg, #6C63FF 0%, #5146FF 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 20px 20px 4px 20px;
        margin: 10px 0 10px auto;
        max-width: 80%;
        font-size: 14.5px;
        line-height: 1.5;
        box-shadow: 0 6px 16px rgba(108, 99, 255, 0.25);
    }}
    .chat-bubble-bot {{
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        color: rgba(255,255,255,0.95);
        padding: 12px 18px;
        border-radius: 20px 20px 20px 4px;
        margin: 10px auto 10px 0;
        max-width: 80%;
        font-size: 14.5px;
        line-height: 1.5;
    }}

    /* 5. Personality Section Stying */
    .personality-pills-container {{
        padding: 12px 16px;
        background: rgba(0,0,0,0.2);
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }}
    
    /* Target Streamlit buttons to look like segmented pills */
    div[data-testid="column"] button {{
        border: none !important;
        background: transparent !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        height: 36px !important;
    }}
    div[data-testid="column"] button:hover {{
        background: rgba(255,255,255,0.05) !important;
    }}

    /* Bottom Input Area */
    div.stForm {{
        background: rgba(0,0,0,0.3) !important;
        border-top: 1px solid rgba(255,255,255,0.08) !important;
        padding: 12px 16px !important;
    }}
    div.stForm [data-testid="stVerticalBlock"] {{
        gap: 0 !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    # ── Floating Avatar Button ────────────────────────
    if st.button("Avatar", key="daybot_avatar_btn"):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun()

    # ── Floating Chat Panel ───────────────────────────
    if st.session_state.chat_open:
        panel_container = st.container()
        with panel_container:
            st.markdown('<div id="daybot-chat-container"></div>', unsafe_allow_html=True)
            import streamlit.components.v1 as components
            components.html("""
                <script>
                    const chatNode = window.parent.document.getElementById('daybot-chat-container');
                    if (chatNode) {
                        const panel = chatNode.closest('[data-testid="stVerticalBlock"]');
                        if (panel) {
                            panel.classList.add("floating-daybot-panel");
                        }
                    }
                </script>
            """, height=0, width=0)
            
            # Header with Close Button handling
            head_col1, head_col2 = st.columns([5, 1])
            with head_col1:
                st.markdown("""
                <div class="daybot-premium-header" style="border-radius: 24px 0 0 0;">
                    <div class="ai-icon-glow">🤖</div>
                    <div>
                        <div style="font-weight:800; color:white; font-size:18px; letter-spacing:-0.5px;">DayBot AI</div>
                        <div style="font-size:12px; color:rgba(255,255,255,0.6); font-weight:500;">Premium Wellness Coach</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with head_col2:
                # Add a little top margin to the close button so it sits well in the header space
                st.markdown("<div style='margin-top: 15px;'>", unsafe_allow_html=True)
                if st.button("✖", key="close_chat_btn", help="Close Chat"):
                    st.session_state.chat_open = False
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            # Behavior / Personality Selection (Premium Pills layout)
            st.markdown("<div style='padding: 8px 16px 4px 16px;'>", unsafe_allow_html=True)
            pill_cols = st.columns(3)
            options = ["Friendly", "Professional", "Rude"]
            
            for i, opt in enumerate(options):
                with pill_cols[i]:
                    is_active = (st.session_state.chat_personality == opt)
                    if st.button(opt, key=f"btn_{opt}", width="stretch", type="primary" if is_active else "secondary"):
                        st.session_state.chat_personality = opt
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            # Chat History Container
            history_col = st.container(height=240, border=False)
            with history_col:
                for msg in st.session_state.chat_history:
                    if msg["role"] == "user":
                        st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-bubble-bot">{msg["content"]}</div>', unsafe_allow_html=True)

            # Footer / Input
            with st.form("daybot_chat_form", clear_on_submit=True, border=False):
                col1, col2 = st.columns([5, 1])
                with col1:
                    prompt = st.text_input(
                        "Message DayBot...",
                        label_visibility="collapsed",
                        placeholder="Ask about your health..."
                    )
                with col2:
                    submitted = st.form_submit_button("➤")
                    
                if submitted and prompt:
                    st.session_state.chat_history.append({"role": "user", "content": prompt})
                    try:
                        from features.chat.chat_logic import generate_response
                        ctx = st.session_state.get("fitness_data", {})
                        reply = generate_response(st.session_state.chat_history, "Friendly", ctx)
                        st.session_state.chat_history.append({"role": "bot", "content": reply})
                    except Exception as e:
                        st.session_state.chat_history.append({"role": "bot", "content": f"Error: {e}"})
                    st.rerun()
