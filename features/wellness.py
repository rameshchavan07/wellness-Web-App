"""
DayScore - Wellness Feature
Breathing exercises, relaxing games, and calming sounds.
"""

import streamlit as st
import time
import random


def render_wellness():
    """Render the Wellness page."""
    st.markdown("""
    <h1 style="font-size:32px; font-weight:800; color:#4ECDC4;">
        🧘 Wellness Center
    </h1>
    <p style="color:rgba(255,255,255,0.5); margin-bottom:24px;">
        Relax, breathe, and recharge with these calming exercises.
    </p>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🌬️ Breathing", "🎮 Games", "🎵 Sounds"])

    with tab1:
        _render_breathing_exercise()

    with tab2:
        _render_games()

    with tab3:
        _render_sounds()


def _render_breathing_exercise():
    """4-4-6 breathing exercise with animated circle."""
    st.markdown("### 🌬️ Breathing Exercise")
    st.markdown("""
    <p style="color:rgba(255,255,255,0.6);">
        Follow the animated circle to practice the <strong>4-4-6 breathing pattern</strong>:<br>
        Inhale for 4 seconds → Hold for 4 seconds → Exhale for 6 seconds
    </p>
    """, unsafe_allow_html=True)

    # Breathing pattern selector
    pattern = st.selectbox("Choose pattern:", [
        "4-4-6 (Calming)",
        "4-7-8 (Sleep Aid)",
        "Box Breathing (4-4-4-4)",
    ])

    if pattern == "4-4-6 (Calming)":
        inhale, hold, exhale = 4, 4, 6
    elif pattern == "4-7-8 (Sleep Aid)":
        inhale, hold, exhale = 4, 7, 8
    else:
        inhale, hold, exhale = 4, 4, 4

    rounds = st.slider("Number of rounds:", 1, 10, 3)

    # Display current settings
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center; padding:16px;">
            <div style="font-size:24px; font-weight:700; color:#4ECDC4;">{inhale}s</div>
            <div style="color:rgba(255,255,255,0.5); font-size:12px;">Inhale</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center; padding:16px;">
            <div style="font-size:24px; font-weight:700; color:#FFD93D;">{hold}s</div>
            <div style="color:rgba(255,255,255,0.5); font-size:12px;">Hold</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center; padding:16px;">
            <div style="font-size:24px; font-weight:700; color:#6C63FF;">{exhale}s</div>
            <div style="color:rgba(255,255,255,0.5); font-size:12px;">Exhale</div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🧘 Start Breathing Exercise", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        circle_display = st.empty()

        total_steps = rounds * (inhale + hold + exhale)
        current_step = 0

        for r in range(rounds):
            # Inhale
            for s in range(inhale):
                current_step += 1
                scale = 1 + (s / inhale) * 0.5
                circle_display.markdown(f"""
                <div style="display:flex; justify-content:center;">
                    <div style="width:{int(150 * scale)}px; height:{int(150 * scale)}px; 
                        border-radius:50%;
                        background: radial-gradient(circle, #4ECDC4, #45B7AA);
                        display:flex; align-items:center; justify-content:center;
                        color:white; font-size:20px; font-weight:600;
                        box-shadow: 0 0 {int(40 * scale)}px rgba(78, 205, 196, 0.4);
                        transition: all 0.8s ease;">
                        Breathe In
                    </div>
                </div>
                """, unsafe_allow_html=True)
                status_text.markdown(f"**Round {r+1}/{rounds}** — 🌬️ Inhaling... ({s+1}/{inhale}s)")
                progress_bar.progress(current_step / total_steps)
                time.sleep(1)

            # Hold
            for s in range(hold):
                current_step += 1
                circle_display.markdown(f"""
                <div style="display:flex; justify-content:center;">
                    <div style="width:225px; height:225px; border-radius:50%;
                        background: radial-gradient(circle, #FFD93D, #FFC107);
                        display:flex; align-items:center; justify-content:center;
                        color:white; font-size:20px; font-weight:600;
                        box-shadow: 0 0 60px rgba(255, 217, 61, 0.4);">
                        Hold
                    </div>
                </div>
                """, unsafe_allow_html=True)
                status_text.markdown(f"**Round {r+1}/{rounds}** — ⏸️ Holding... ({s+1}/{hold}s)")
                progress_bar.progress(current_step / total_steps)
                time.sleep(1)

            # Exhale
            for s in range(exhale):
                current_step += 1
                scale = 1.5 - (s / exhale) * 0.5
                circle_display.markdown(f"""
                <div style="display:flex; justify-content:center;">
                    <div style="width:{int(150 * scale)}px; height:{int(150 * scale)}px; 
                        border-radius:50%;
                        background: radial-gradient(circle, #6C63FF, #5a52e0);
                        display:flex; align-items:center; justify-content:center;
                        color:white; font-size:20px; font-weight:600;
                        box-shadow: 0 0 {int(40 * scale)}px rgba(108, 99, 255, 0.4);
                        transition: all 0.8s ease;">
                        Breathe Out
                    </div>
                </div>
                """, unsafe_allow_html=True)
                status_text.markdown(f"**Round {r+1}/{rounds}** — 💨 Exhaling... ({s+1}/{exhale}s)")
                progress_bar.progress(current_step / total_steps)
                time.sleep(1)

        circle_display.empty()
        status_text.empty()
        progress_bar.empty()
        st.success("🎉 Great job! You completed the breathing exercise. Feel the calm!")
        st.balloons()


def _render_games():
    """Relaxing mini-games."""
    st.markdown("### 🎮 Relaxing Games")

    game = st.selectbox("Choose a game:", ["⚡ Reaction Time", "🧠 Memory Game", "🔢 Number Zen"])

    if game == "⚡ Reaction Time":
        _reaction_game()
    elif game == "🧠 Memory Game":
        _memory_game()
    else:
        _number_zen_game()


def _reaction_game():
    """Simple reaction time test."""
    st.markdown("""
    <div class="metric-card">
        <h4 style="color:white;">⚡ Reaction Time Test</h4>
        <p style="color:rgba(255,255,255,0.6);">
            Click the button as quickly as you can when the color changes to green!
        </p>
    </div>
    """, unsafe_allow_html=True)

    if "reaction_state" not in st.session_state:
        st.session_state.reaction_state = "ready"
        st.session_state.reaction_times = []

    if st.session_state.reaction_state == "ready":
        if st.button("🟡 Click to Start!", use_container_width=True):
            st.session_state.reaction_state = "waiting"
            st.session_state.reaction_start = time.time() + random.uniform(1, 4)
            st.rerun()

    elif st.session_state.reaction_state == "waiting":
        elapsed = time.time() - st.session_state.reaction_start
        if elapsed >= 0:
            st.session_state.reaction_state = "go"
            st.session_state.reaction_go_time = time.time()
            st.rerun()
        else:
            st.warning("⏳ Wait for the green signal...")
            time.sleep(0.5)
            st.rerun()

    elif st.session_state.reaction_state == "go":
        if st.button("🟢 CLICK NOW!", use_container_width=True):
            reaction_time = int((time.time() - st.session_state.reaction_go_time) * 1000)
            st.session_state.reaction_times.append(reaction_time)

            if reaction_time < 300:
                st.success(f"⚡ Amazing! {reaction_time}ms — Lightning fast!")
            elif reaction_time < 500:
                st.success(f"👍 Good! {reaction_time}ms — Nice reflexes!")
            else:
                st.info(f"🐢 {reaction_time}ms — Keep practicing!")

            if st.session_state.reaction_times:
                avg = sum(st.session_state.reaction_times) / len(st.session_state.reaction_times)
                st.markdown(f"📊 **Average:** {int(avg)}ms over {len(st.session_state.reaction_times)} attempts")

            st.session_state.reaction_state = "ready"


def _memory_game():
    """Pattern memory game."""
    st.markdown("""
    <div class="metric-card">
        <h4 style="color:white;">🧠 Memory Game</h4>
        <p style="color:rgba(255,255,255,0.6);">
            Remember the sequence of colors and repeat it!
        </p>
    </div>
    """, unsafe_allow_html=True)

    colors = ["🔴", "🔵", "🟢", "🟡", "🟣"]

    if "memory_sequence" not in st.session_state:
        st.session_state.memory_sequence = []
        st.session_state.memory_round = 0
        st.session_state.memory_input = []
        st.session_state.memory_phase = "start"

    if st.session_state.memory_phase == "start":
        st.markdown(f"**Current Level:** {st.session_state.memory_round}")
        if st.button("🎮 Start / Next Round", use_container_width=True):
            st.session_state.memory_round += 1
            st.session_state.memory_sequence.append(random.choice(colors))
            st.session_state.memory_phase = "show"
            st.session_state.memory_input = []
            st.rerun()

    elif st.session_state.memory_phase == "show":
        st.markdown(f"### 👀 Memorize this sequence (Level {st.session_state.memory_round}):")
        seq_display = " → ".join(st.session_state.memory_sequence)
        st.markdown(f"""
        <div style="text-align:center; padding:20px; background:rgba(108,99,255,0.1); 
            border-radius:12px; font-size:32px; letter-spacing:8px;">
            {seq_display}
        </div>
        """, unsafe_allow_html=True)

        if st.button("✅ I memorized it!", use_container_width=True):
            st.session_state.memory_phase = "input"
            st.rerun()

    elif st.session_state.memory_phase == "input":
        st.markdown(f"### 🎯 Repeat the sequence (Level {st.session_state.memory_round}):")
        st.markdown(f"Selected: {' → '.join(st.session_state.memory_input)}")

        cols = st.columns(5)
        for i, color in enumerate(colors):
            with cols[i]:
                if st.button(color, key=f"mem_{color}_{len(st.session_state.memory_input)}"):
                    st.session_state.memory_input.append(color)
                    idx = len(st.session_state.memory_input) - 1

                    if st.session_state.memory_input[idx] != st.session_state.memory_sequence[idx]:
                        st.error(f"❌ Wrong! The correct sequence was: {' → '.join(st.session_state.memory_sequence)}")
                        st.markdown(f"🏆 **You reached Level {st.session_state.memory_round - 1}!**")
                        st.session_state.memory_sequence = []
                        st.session_state.memory_round = 0
                        st.session_state.memory_input = []
                        st.session_state.memory_phase = "start"
                    elif len(st.session_state.memory_input) == len(st.session_state.memory_sequence):
                        st.success(f"✅ Correct! Level {st.session_state.memory_round} complete!")
                        st.session_state.memory_phase = "start"
                    st.rerun()

    if st.button("🔄 Reset Game"):
        st.session_state.memory_sequence = []
        st.session_state.memory_round = 0
        st.session_state.memory_input = []
        st.session_state.memory_phase = "start"
        st.rerun()


def _number_zen_game():
    """Calming number sequence game."""
    st.markdown("""
    <div class="metric-card">
        <h4 style="color:white;">🔢 Number Zen</h4>
        <p style="color:rgba(255,255,255,0.6);">
            Find and click numbers in ascending order as quickly as you can. 
            A calming focus exercise!
        </p>
    </div>
    """, unsafe_allow_html=True)

    grid_size = st.slider("Grid size:", 3, 6, 4)

    if "zen_numbers" not in st.session_state or st.button("🔄 New Game"):
        nums = list(range(1, grid_size * grid_size + 1))
        random.shuffle(nums)
        st.session_state.zen_numbers = nums
        st.session_state.zen_next = 1
        st.session_state.zen_found = set()

    numbers = st.session_state.zen_numbers
    next_num = st.session_state.zen_next
    found = st.session_state.zen_found
    total = grid_size * grid_size

    st.markdown(f"**Find:** {next_num} / {total}")
    st.progress(len(found) / total)

    for row in range(grid_size):
        cols = st.columns(grid_size)
        for col_idx in range(grid_size):
            idx = row * grid_size + col_idx
            num = numbers[idx]
            with cols[col_idx]:
                if num in found:
                    st.markdown(f"""
                    <div style="text-align:center; padding:12px; background:rgba(78,205,196,0.2); 
                        border-radius:8px; color:#4ECDC4; font-weight:700;">✓</div>
                    """, unsafe_allow_html=True)
                else:
                    if st.button(str(num), key=f"zen_{idx}"):
                        if num == next_num:
                            st.session_state.zen_found.add(num)
                            st.session_state.zen_next += 1
                            if len(st.session_state.zen_found) == total:
                                st.success("🎉 Congratulations! You found all numbers!")
                                st.balloons()
                            st.rerun()


def _render_sounds():
    """Relaxing sounds section."""
    st.markdown("### 🎵 Relaxing Sounds")
    st.markdown("""
    <p style="color:rgba(255,255,255,0.6);">
        Choose a calming soundscape to help you relax and focus.
    </p>
    """, unsafe_allow_html=True)

    sounds = {
        "🌧️ Rain": {
            "description": "Gentle rainfall to calm your mind",
            "frequency": "Natural",
            "color": "#4ECDC4",
            "url": "https://www.youtube.com/watch?v=q76bMs-NwRk"
        },
        "🌲 Forest": {
            "description": "Birds chirping and wind through trees",
            "frequency": "Natural",
            "color": "#45B7AA",
            "url": "https://www.youtube.com/watch?v=xNN7iTA57jM"
        },
        "📻 White Noise": {
            "description": "Steady white noise for focus",
            "frequency": "All frequencies",
            "color": "#6C63FF",
            "url": "https://www.youtube.com/watch?v=nMfPqeZjc2c"
        },
        "🎵 432Hz Tone": {
            "description": "The 'healing frequency' for deep relaxation",
            "frequency": "432 Hz",
            "color": "#FFD93D",
            "url": "https://www.youtube.com/watch?v=1ZYbU82GVz4"
        },
        "🎶 528Hz Tone": {
            "description": "The 'love frequency' for stress reduction",
            "frequency": "528 Hz",
            "color": "#FF6B6B",
            "url": "https://www.youtube.com/watch?v=hkmMWGE8o50"
        },
        "🌊 Ocean Waves": {
            "description": "Rhythmic waves gently crashing on shore",
            "frequency": "Natural",
            "color": "#5B9BD5",
            "url": "https://www.youtube.com/watch?v=f77SKdyn-1Y"
        },
    }

    cols = st.columns(3)
    for i, (name, info) in enumerate(sounds.items()):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center; border-color:{info['color']}33;">
                <div style="font-size:42px; margin-bottom:8px;">{name.split(' ')[0]}</div>
                <div style="font-weight:600; color:white; font-size:15px;">{name.split(' ', 1)[1]}</div>
                <div style="color:rgba(255,255,255,0.5); font-size:12px; margin-top:4px;">
                    {info['description']}
                </div>
                <div style="color:{info['color']}; font-size:11px; margin-top:8px;">
                    {info['frequency']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    selected_sound = st.selectbox(
        "Select a sound to play:",
        list(sounds.keys()),
    )

    if "playing_sound" not in st.session_state:
        st.session_state.playing_sound = None

    if st.button("▶️ Load & Play Sound", use_container_width=True):
        st.session_state.playing_sound = selected_sound
        st.rerun()

    if st.session_state.playing_sound:
        st.markdown(f"### Now Playing: {st.session_state.playing_sound}")
        st.video(sounds[st.session_state.playing_sound]["url"])

    # Duration control
    st.markdown("---")
    duration = st.slider("Session Duration (minutes):", 1, 60, 15)
    st.markdown(f"""
    <div class="metric-card" style="text-align:center;">
        <div style="font-size:14px; color:rgba(255,255,255,0.5);">Session Duration</div>
        <div style="font-size:32px; font-weight:700; color:#6C63FF;">{duration} min</div>
        <div style="color:rgba(255,255,255,0.4); font-size:12px; margin-top:4px;">
            Perfect for a quick relaxation break
        </div>
    </div>
    """, unsafe_allow_html=True)
