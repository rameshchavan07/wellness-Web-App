import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
from features.chat.chat_ui import render_floating_chat

# Set page config for standard looking Streamlit page
st.set_page_config(
    page_title="DayScore - Wellness App",
    page_icon="🌿",
    layout="wide"
)

def main():
    st.title("🌿 DayScore Wellness Dashboard")
    st.write("Welcome to the DayScore main page!")
    
    st.info("Notice the floating chat widget at the bottom right corner? Click it to start chatting!")
    
    # Just to show that normal Streamlit layout exists behind it
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Daily Steps", value="8,432", delta="1,200")
        
    with col2:
        st.metric(label="Calories Burned", value="2,100", delta="-300")
        
    with col3:
        st.metric(label="Sleep Score", value="85", delta="5")
        
    st.divider()
    
    st.subheader("How to integrate the widget:")
    st.code('''
# In your main app.py or any page where you want the chat to appear:

from features.chat.chat_ui import render_floating_chat

def main():
    st.title("My App")
    
    # Render the widget globally
    render_floating_chat()
    
if __name__ == "__main__":
    main()
    ''', language='python')
    
    # Render the chat widget!
    render_floating_chat()

if __name__ == "__main__":
    main()
