"""
DayScore - Chatbot Feature
AI wellness chatbot interface.
"""

import streamlit as st
from services.chatbot_service import ChatbotService


def render_chatbot():
    """Render the AI Chatbot page."""
    user = st.session_state.get("user", {})
    user_id = user.get("user_id", "demo_user_001")

    st.markdown("""
    <h1 style="font-size:32px; font-weight:800;
        background: linear-gradient(90deg, #6C63FF, #FF6B6B);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        🤖 AI Wellness Coach
    </h1>
    <p style="color:rgba(255,255,255,0.5); margin-bottom:16px;">
        Ask me anything about workouts, nutrition, sleep, or mental health!
    </p>
    """, unsafe_allow_html=True)

    chatbot = ChatbotService()

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": "👋 Hi! I'm your DayScore AI wellness coach. "
                           "I can help with workout suggestions, sleep tips, "
                           "stress management, and nutrition advice. What's on your mind?",
            }
        ]

    # Quick action buttons
    st.markdown("#### 💡 Quick Questions")
    quick_questions = [
        "💪 Suggest a quick workout",
        "😴 Help me sleep better",
        "🧘 Stress relief tips",
        "🥗 Healthy meal ideas",
        "🚶 How to walk more",
    ]

    cols = st.columns(len(quick_questions))
    for i, q in enumerate(quick_questions):
        with cols[i]:
            if st.button(q, key=f"quick_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": q})
                # Get user context for personalization
                user_context = {}
                if "fitness_data" in st.session_state:
                    user_context = st.session_state.fitness_data
                response = chatbot.get_response(q, user_context)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                chatbot.save_chat_message(user_id, "user", q)
                chatbot.save_chat_message(user_id, "assistant", response)
                st.rerun()

    st.markdown("---")

    # Chat display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="display:flex; justify-content:flex-end; margin:8px 0;">
                    <div class="chat-user">{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex; justify-content:flex-start; margin:8px 0;">
                    <div class="chat-ai">
                        <span style="color:#6C63FF; font-weight:600;">🤖 DayScore AI</span><br>
                        {msg['content']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Chat input
    st.markdown("")
    user_input = st.chat_input("Ask me about health, fitness, or wellness...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Build user context
        user_context = {}
        if "fitness_data" in st.session_state:
            user_context = st.session_state.fitness_data

        with st.spinner("🤔 Thinking..."):
            response = chatbot.get_response(user_input, user_context)

        st.session_state.chat_history.append({"role": "assistant", "content": response})

        # Save to Firestore
        chatbot.save_chat_message(user_id, "user", user_input)
        chatbot.save_chat_message(user_id, "assistant", response)

        st.rerun()

    # Clear chat button
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = [
                {
                    "role": "assistant",
                    "content": "👋 Chat cleared! How can I help you today?",
                }
            ]
            st.rerun()

    # Tips
    with st.expander("ℹ️ Tips for best results"):
        st.markdown("""
        - **Be specific** — "Suggest a 15-minute home workout" works better than "workout"
        - **Share context** — "I've been sitting all day, what should I do?"
        - **Ask follow-ups** — "Can you make that workout easier?"
        - **Try topics** — Workouts, sleep, stress, nutrition, hydration, meditation
        """)
