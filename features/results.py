"""
DayScore - Results & Insights Feature
Analytics page with trends, stats, and personalized suggestions.
"""

import streamlit as st
import plotly.graph_objects as go

from services.scoring_service import ScoringService
from services.google_fit_service import GoogleFitService
from utils.helpers import (
    generate_weekly_demo_scores,
    calculate_stats,
    get_date_labels,
    get_personalized_suggestions,
)


def render_results():
    """Render the Results & Insights page."""
    st.markdown("""
    <h1 style="font-size:32px; font-weight:800;
        background: linear-gradient(90deg, #4ECDC4, #6C63FF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
        📈 Results & Insights
    </h1>
    <p style="color:rgba(255,255,255,0.5); margin-bottom:24px;">
        Dive deep into your health data and discover trends.
    </p>
    """, unsafe_allow_html=True)

    # Get weekly data
    scoring_service = ScoringService()
    fit_service = GoogleFitService()
    google_creds = st.session_state.get("google_fit_credentials", {})

    weekly_raw = fit_service.fetch_weekly_data(google_creds)
    weekly_scores = []
    weekly_steps = []
    weekly_sleep = []
    weekly_calories = []

    for day_data in weekly_raw:
        result = scoring_service.calculate_score(day_data)
        weekly_scores.append(result["total_score"])
        weekly_steps.append(day_data.get("steps", 0))
        weekly_sleep.append(day_data.get("sleep", 0))
        weekly_calories.append(day_data.get("calories", 0))

    labels = get_date_labels(7)
    stats = calculate_stats(weekly_scores)

    # ── Summary Cards ──────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <div style="font-size:14px; color:rgba(255,255,255,0.5);">Best Score</div>
            <div style="font-size:36px; font-weight:800; color:#4ECDC4;">{stats['best']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <div style="font-size:14px; color:rgba(255,255,255,0.5);">Average</div>
            <div style="font-size:36px; font-weight:800; color:#6C63FF;">{stats['average']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <div style="font-size:14px; color:rgba(255,255,255,0.5);">Lowest</div>
            <div style="font-size:36px; font-weight:800; color:#FF6B6B;">{stats['worst']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        trend_icons = {"improving": "📈", "declining": "📉", "stable": "➡️"}
        trend_colors = {"improving": "#4ECDC4", "declining": "#FF6B6B", "stable": "#FFD93D"}
        trend = stats["trend"]
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <div style="font-size:14px; color:rgba(255,255,255,0.5);">Trend</div>
            <div style="font-size:36px; font-weight:800; color:{trend_colors[trend]};">
                {trend_icons[trend]}
            </div>
            <div style="font-size:13px; color:{trend_colors[trend]}; text-transform:capitalize;">{trend}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Score Trend Chart ──────────────────────────────
    st.markdown("---")
    st.markdown("### 📊 Weekly Score Trend")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=weekly_scores,
        mode="lines+markers+text",
        text=[f"{s}" for s in weekly_scores],
        textposition="top center",
        textfont=dict(size=11, color="rgba(255,255,255,0.7)", family="Inter"),
        line=dict(color="#6C63FF", width=3, shape="spline"),
        marker=dict(size=10, color="#6C63FF", line=dict(width=2, color="white")),
        fill="tozeroy",
        fillcolor="rgba(108, 99, 255, 0.08)",
    ))
    # Add target line at 80
    fig.add_hline(y=80, line_dash="dash", line_color="rgba(78,205,196,0.4)",
                  annotation_text="Target (80)", annotation_font_color="rgba(78,205,196,0.6)")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, color="rgba(255,255,255,0.5)", tickfont=dict(family="Inter")),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", range=[0, 105],
                   color="rgba(255,255,255,0.5)", tickfont=dict(family="Inter")),
        height=350, margin=dict(l=40, r=20, t=30, b=40),
        showlegend=False, font=dict(family="Inter"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Detailed Metrics ───────────────────────────────
    st.markdown("### 📋 Detailed Metrics")

    tab1, tab2, tab3 = st.tabs(["🚶 Steps", "😴 Sleep", "🔥 Calories"])

    with tab1:
        fig_steps = go.Figure(go.Bar(
            x=labels, y=weekly_steps,
            marker=dict(color="#6C63FF", cornerradius=6),
            text=weekly_steps, textposition="outside",
            textfont=dict(color="rgba(255,255,255,0.7)", family="Inter"),
        ))
        fig_steps.add_hline(y=10000, line_dash="dash", line_color="rgba(78,205,196,0.4)",
                            annotation_text="Goal (10k)")
        fig_steps.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, color="rgba(255,255,255,0.5)"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="rgba(255,255,255,0.5)"),
            height=300, margin=dict(l=40, r=20, t=20, b=40),
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig_steps, use_container_width=True, config={"displayModeBar": False})

        avg_steps = sum(weekly_steps) / len(weekly_steps) if weekly_steps else 0
        st.info(f"📊 **Weekly average:** {int(avg_steps):,} steps/day | **Goal:** 10,000 steps")

    with tab2:
        fig_sleep = go.Figure(go.Bar(
            x=labels, y=weekly_sleep,
            marker=dict(color="#4ECDC4", cornerradius=6),
            text=[f"{s}h" for s in weekly_sleep], textposition="outside",
            textfont=dict(color="rgba(255,255,255,0.7)", family="Inter"),
        ))
        fig_sleep.add_hrect(y0=7, y1=8, fillcolor="rgba(78,205,196,0.1)",
                            line_width=0, annotation_text="Ideal (7-8h)")
        fig_sleep.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, color="rgba(255,255,255,0.5)"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="rgba(255,255,255,0.5)"),
            height=300, margin=dict(l=40, r=20, t=20, b=40),
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig_sleep, use_container_width=True, config={"displayModeBar": False})

        avg_sleep = sum(weekly_sleep) / len(weekly_sleep) if weekly_sleep else 0
        st.info(f"😴 **Weekly average:** {avg_sleep:.1f} hours/night | **Ideal:** 7-8 hours")

    with tab3:
        fig_cal = go.Figure(go.Bar(
            x=labels, y=weekly_calories,
            marker=dict(color="#FFD93D", cornerradius=6),
            text=weekly_calories, textposition="outside",
            textfont=dict(color="rgba(255,255,255,0.7)", family="Inter"),
        ))
        fig_cal.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, color="rgba(255,255,255,0.5)"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="rgba(255,255,255,0.5)"),
            height=300, margin=dict(l=40, r=20, t=20, b=40),
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig_cal, use_container_width=True, config={"displayModeBar": False})

        avg_cal = sum(weekly_calories) / len(weekly_calories) if weekly_calories else 0
        st.info(f"🔥 **Weekly average:** {int(avg_cal):,} calories/day")

    # ── Suggestions ────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💡 What to Improve")

    # Use today's breakdown for suggestions
    today_data = weekly_raw[-1] if weekly_raw else {}
    today_result = scoring_service.calculate_score(today_data)
    suggestions = get_personalized_suggestions(today_result.get("breakdown", {}))

    for sug in suggestions:
        st.markdown(f"""
        <div class="metric-card" style="display:flex; align-items:center; gap:16px;">
            <div style="font-size:36px;">{sug['icon']}</div>
            <div>
                <div style="font-weight:600; color:white;">{sug['title']}</div>
                <div style="color:rgba(255,255,255,0.6); font-size:14px;">{sug['tip']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
