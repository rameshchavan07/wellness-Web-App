"""
DayScore - UI Components
Reusable Streamlit UI components and styling.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


def inject_custom_css():
    """Inject global custom CSS for premium look and feel."""
    st.markdown("""
    <style>
    /* ── Global Styles ─────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0E1117 0%, #1A1D26 50%, #0E1117 100%);
    }

    /* ── Cards ──────────────────────────────────────────── */
    .metric-card {
        background: linear-gradient(145deg, rgba(108, 99, 255, 0.1), rgba(108, 99, 255, 0.03));
        border: 1px solid rgba(108, 99, 255, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin: 8px 0;
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(108, 99, 255, 0.2);
    }

    .score-card {
        background: linear-gradient(135deg, #6C63FF 0%, #4ECDC4 100%);
        border-radius: 20px;
        padding: 32px;
        text-align: center;
        color: white;
        box-shadow: 0 12px 40px rgba(108, 99, 255, 0.3);
    }

    .achievement-badge {
        background: linear-gradient(145deg, rgba(78, 205, 196, 0.15), rgba(78, 205, 196, 0.05));
        border: 1px solid rgba(78, 205, 196, 0.3);
        border-radius: 12px;
        padding: 16px;
        margin: 6px 0;
        text-align: center;
        transition: all 0.3s ease;
    }
    .achievement-badge:hover {
        transform: scale(1.03);
        box-shadow: 0 4px 20px rgba(78, 205, 196, 0.25);
    }

    .achievement-locked {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        margin: 6px 0;
        text-align: center;
        opacity: 0.5;
    }

    /* ── Leaderboard ───────────────────────────────────── */
    .leaderboard-row {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        padding: 12px 16px;
        margin: 4px 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .leaderboard-row.top-3 {
        background: linear-gradient(90deg, rgba(255, 215, 0, 0.1), transparent);
        border-left: 3px solid #FFD700;
    }

    /* ── Challenge Card ────────────────────────────────── */
    .challenge-card {
        background: linear-gradient(145deg, rgba(255, 107, 107, 0.1), rgba(255, 107, 107, 0.03));
        border: 1px solid rgba(255, 107, 107, 0.2);
        border-radius: 16px;
        padding: 20px;
        margin: 8px 0;
    }

    /* ── Breathing Circle ──────────────────────────────── */
    @keyframes breatheIn {
        0% { transform: scale(1); opacity: 0.6; }
        100% { transform: scale(1.5); opacity: 1; }
    }
    @keyframes breatheOut {
        0% { transform: scale(1.5); opacity: 1; }
        100% { transform: scale(1); opacity: 0.6; }
    }
    .breathing-circle {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        background: radial-gradient(circle, #6C63FF, #4ECDC4);
        margin: 40px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 24px;
        font-weight: 600;
        box-shadow: 0 0 60px rgba(108, 99, 255, 0.4);
    }

    /* ── Notification Cards ────────────────────────────── */
    .notif-card {
        border-radius: 10px;
        padding: 12px;
        margin: 4px 0;
        font-size: 14px;
    }

    /* ── Sidebar Styling ───────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #131620 0%, #1A1D26 100%);
        border-right: 1px solid rgba(108, 99, 255, 0.15);
    }

    /* ── Buttons ───────────────────────────────────────── */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(108, 99, 255, 0.3);
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, rgba(108, 99, 255, 0.6), rgba(78, 205, 196, 0.4)) !important;
        color: white !important;
        border: 1px solid rgba(108, 99, 255, 0.8) !important;
    }


    /* ── Progress bar custom ───────────────────────────── */
    .custom-progress {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        height: 12px;
        overflow: hidden;
        margin: 4px 0;
    }
    .custom-progress-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 1s ease;
    }

    /* ── Chat Messages ─────────────────────────────────── */
    .chat-user {
        background: linear-gradient(135deg, #6C63FF, #5a52e0);
        border-radius: 16px 16px 4px 16px;
        padding: 12px 16px;
        margin: 4px 0;
        color: white;
        max-width: 80%;
        margin-left: auto;
    }
    .chat-ai {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px 16px 16px 4px;
        padding: 12px 16px;
        margin: 4px 0;
        max-width: 80%;
    }

    /* ── Hide Streamlit defaults ───────────────────────── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { background: transparent !important; }
    </style>
    """, unsafe_allow_html=True)


def render_score_gauge(score: float, grade: str):
    """Render a circular DayScore gauge using Plotly."""
    # Determine color based on score
    if score >= 80:
        color = "#4ECDC4"
    elif score >= 60:
        color = "#FFD93D"
    elif score >= 40:
        color = "#FF8C42"
    else:
        color = "#FF6B6B"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "", "font": {"size": 52, "color": "white", "family": "Inter"}},
        title={"text": f"Grade: {grade}", "font": {"size": 18, "color": "rgba(255,255,255,0.7)"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": "rgba(0,0,0,0)"},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "rgba(255,255,255,0.05)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "rgba(255, 107, 107, 0.1)"},
                {"range": [40, 60], "color": "rgba(255, 140, 66, 0.1)"},
                {"range": [60, 80], "color": "rgba(255, 217, 61, 0.1)"},
                {"range": [80, 100], "color": "rgba(78, 205, 196, 0.1)"},
            ],
            "threshold": {
                "line": {"color": "white", "width": 2},
                "thickness": 0.8,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=280,
        margin=dict(l=30, r=30, t=50, b=10),
        font={"family": "Inter"},
    )
    return fig


def render_metric_card(icon: str, label: str, value, score: float, color: str):
    """Render a styled metric card with progress bar."""
    pct = min(score, 100)
    st.markdown(f"""
    <div class="metric-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span style="font-size:14px; color:rgba(255,255,255,0.7);">{icon} {label}</span>
            <span style="font-size:20px; font-weight:700; color:white;">{value}</span>
        </div>
        <div class="custom-progress">
            <div class="custom-progress-fill" style="width:{pct}%; background: linear-gradient(90deg, {color}, {color}88);"></div>
        </div>
        <div style="text-align:right; margin-top:4px;">
            <span style="font-size:12px; color:rgba(255,255,255,0.5);">Score: {score}/100</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_weekly_chart(weekly_scores: list, labels: list):
    """Render a weekly score trend chart."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=labels,
        y=weekly_scores,
        mode="lines+markers",
        line=dict(color="#6C63FF", width=3, shape="spline"),
        marker=dict(size=10, color="#6C63FF", line=dict(width=2, color="white")),
        fill="tozeroy",
        fillcolor="rgba(108, 99, 255, 0.1)",
        name="DayScore",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            showgrid=False,
            color="rgba(255,255,255,0.5)",
            tickfont=dict(family="Inter"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            range=[0, 100],
            color="rgba(255,255,255,0.5)",
            tickfont=dict(family="Inter"),
        ),
        height=300,
        margin=dict(l=40, r=20, t=20, b=40),
        font=dict(family="Inter"),
        showlegend=False,
    )
    return fig


def render_breakdown_chart(breakdown: dict):
    """Render a horizontal bar chart for score breakdown."""
    categories = []
    scores = []
    colors = []
    color_map = {
        "steps": "#6C63FF",
        "sleep": "#4ECDC4",
        "calories": "#FFD93D",
        "heart_rate": "#FF6B6B",
    }
    emoji_map = {
        "steps": "🚶",
        "sleep": "😴",
        "calories": "🔥",
        "heart_rate": "❤️",
    }

    for key, data in breakdown.items():
        categories.append(f"{emoji_map.get(key, '')} {key.replace('_', ' ').title()}")
        scores.append(data["score"])
        colors.append(color_map.get(key, "#6C63FF"))

    fig = go.Figure(go.Bar(
        x=scores,
        y=categories,
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(width=0),
            cornerradius=6,
        ),
        text=[f"{s}" for s in scores],
        textposition="auto",
        textfont=dict(color="white", family="Inter", size=13),
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            range=[0, 100],
            color="rgba(255,255,255,0.5)",
            tickfont=dict(family="Inter"),
        ),
        yaxis=dict(
            showgrid=False,
            color="rgba(255,255,255,0.8)",
            tickfont=dict(family="Inter", size=13),
        ),
        height=220,
        margin=dict(l=120, r=20, t=10, b=30),
        font=dict(family="Inter"),
    )
    return fig
