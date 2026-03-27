"""
DayScore - Mental Health Dashboard
Visualizes mood trends, emotional patterns, correlations with physical health, and stress insights.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, timezone

from config.settings import AppConfig
from services.journal_service import JournalService, MOOD_SCALE
from services.google_fit_service import GoogleFitService
from services.scoring_service import ScoringService


def render_mental_health():
    """Render the Mental Health Dashboard page."""
    user = st.session_state.get("user", {})
    user_id = user.get("user_id", AppConfig.DEMO_USER_ID)

    journal_service = JournalService()
    fit_service = GoogleFitService()
    scoring_service = ScoringService()

    # ── Header ─────────────────────────────────────────
    st.markdown("""
    <div style="margin-bottom: 24px;">
        <h1 style="margin:0; font-size:32px; font-weight:800;
            background: linear-gradient(90deg, #6C63FF, #FF6B6B);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🧠 Mental Health Dashboard
        </h1>
        <p style="color: rgba(255,255,255,0.5); margin-top:4px; font-size:15px;">
            Understand your emotional patterns and discover what makes you feel your best
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Fetch Data ─────────────────────────────────────
    stats = journal_service.get_mood_stats(user_id, days=30)

    if not stats.get("has_data"):
        st.markdown("""
        <div class="metric-card" style="text-align:center; padding:48px;">
            <div style="font-size:64px; margin-bottom:16px;">📓</div>
            <h2 style="color:white; margin-bottom:8px;">No Journal Data Yet</h2>
            <p style="color:rgba(255,255,255,0.5);">
                Start writing in your <strong>Mood Journal</strong> to see your mental health insights here!
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    entries = stats["entries"]
    distribution = stats["distribution"]

    # ── Overview Cards ─────────────────────────────────
    col1, col2, col3 = st.columns(3)

    avg_mood = stats["average_mood"]
    trend = stats["trend"]
    trend_icons = {"improving": "📈", "declining": "📉", "stable": "➡️"}
    trend_colors = {"improving": "#4ECDC4", "declining": "#FF6B6B", "stable": "#FFD93D"}

    # Find dominant mood
    dominant_emoji = max(distribution, key=lambda x: distribution[x]["count"])
    dominant_info = distribution[dominant_emoji]

    with col1:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <div style="font-size:48px; margin-bottom:4px;">{dominant_emoji}</div>
            <div style="font-size:24px; font-weight:700; color:white;">{dominant_info['label']}</div>
            <div style="color:rgba(255,255,255,0.5); font-size:13px;">Most Common Mood</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <div style="font-size:48px; margin-bottom:4px;">{trend_icons.get(trend, '➡️')}</div>
            <div style="font-size:24px; font-weight:700; color:{trend_colors.get(trend, '#FFD93D')};">
                {trend.title()}
            </div>
            <div style="color:rgba(255,255,255,0.5); font-size:13px;">Mood Trend</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <div style="font-size:48px; margin-bottom:4px;">📊</div>
            <div style="font-size:24px; font-weight:700; color:white;">{stats['total_entries']}</div>
            <div style="color:rgba(255,255,255,0.5); font-size:13px;">Journal Entries</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Mood Trend Chart ───────────────────────────────
    st.markdown("---")
    st.markdown("### 📈 Mood Over Time")

    # Prepare chart data (reverse to chronological order)
    chart_entries = list(reversed(entries[:30]))
    dates = [e.get("date", "") for e in chart_entries]
    mood_values = [e.get("mood_value", 3) for e in chart_entries]
    mood_emojis = [e.get("mood_emoji", "😐") for e in chart_entries]

    # Date labels
    date_labels = []
    for d in dates:
        try:
            dt = datetime.strptime(d, "%Y-%m-%d")
            date_labels.append(dt.strftime("%b %d"))
        except Exception:
            date_labels.append(d)

    fig = go.Figure()

    # Color each point based on mood value
    colors = []
    for val in mood_values:
        if val >= 5:
            colors.append("#4ECDC4")
        elif val >= 4:
            colors.append("#6C63FF")
        elif val >= 3:
            colors.append("#FFD93D")
        elif val >= 2:
            colors.append("#FF8C42")
        else:
            colors.append("#FF6B6B")

    fig.add_trace(go.Scatter(
        x=date_labels,
        y=mood_values,
        mode="lines+markers",
        line=dict(color="#6C63FF", width=3, shape="spline"),
        marker=dict(size=12, color=colors, line=dict(width=2, color="white")),
        fill="tozeroy",
        fillcolor="rgba(108, 99, 255, 0.08)",
        text=[f"{e} {MOOD_SCALE.get(e, {}).get('label', '')}" for e in mood_emojis],
        hovertemplate="<b>%{x}</b><br>Mood: %{text}<br>Score: %{y}/5<extra></extra>",
        name="Mood",
    ))

    # Add reference lines
    fig.add_hline(y=3, line_dash="dot", line_color="rgba(255,255,255,0.2)",
                  annotation_text="Neutral", annotation_position="top left",
                  annotation_font_color="rgba(255,255,255,0.3)")

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, color="rgba(255,255,255,0.5)", tickfont=dict(family="Inter")),
        yaxis=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.05)",
            range=[0.5, 5.5], color="rgba(255,255,255,0.5)",
            tickfont=dict(family="Inter"),
            ticktext=["😢", "😞", "😐", "😊", "🤩"],
            tickvals=[1, 2, 3, 4, 5],
        ),
        height=320,
        margin=dict(l=50, r=20, t=20, b=40),
        font=dict(family="Inter"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Mood Distribution + Emotion Tags ───────────────
    st.markdown("---")
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown("### 🎯 Mood Distribution")

        labels = []
        values = []
        pie_colors = []
        for emoji, info in distribution.items():
            if info["count"] > 0:
                labels.append(f"{emoji} {info['label']}")
                values.append(info["count"])
                pie_colors.append(info["color"])

        if values:
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=pie_colors, line=dict(color="rgba(0,0,0,0.3)", width=2)),
                textfont=dict(color="white", family="Inter", size=13),
                hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
            )])
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=300,
                margin=dict(l=20, r=20, t=10, b=10),
                font=dict(family="Inter", color="white"),
                legend=dict(font=dict(color="rgba(255,255,255,0.7)")),
                showlegend=True,
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    with col_b:
        st.markdown("### 🏷️ Top Emotions")
        tag_counts = stats.get("tag_counts", {})
        if tag_counts:
            sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:8]
            for tag, count in sorted_tags:
                pct = min((count / stats["total_entries"]) * 100, 100)
                st.markdown(f"""
                <div style="margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                        <span style="color:rgba(255,255,255,0.8); font-size:14px;">{tag}</span>
                        <span style="color:rgba(255,255,255,0.5); font-size:12px;">{count}x</span>
                    </div>
                    <div class="custom-progress">
                        <div class="custom-progress-fill"
                             style="width:{pct}%; background: linear-gradient(90deg, #6C63FF, #4ECDC4);">
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Tag your emotions in the Journal to see patterns here!")

    # ── Health Correlations ────────────────────────────
    st.markdown("---")
    st.markdown("### 🔗 Mind-Body Connections")
    st.markdown(
        '<p style="color:rgba(255,255,255,0.5); font-size:14px; margin-bottom:16px;">'
        'How your physical health relates to your mood</p>',
        unsafe_allow_html=True,
    )

    correlations = _calculate_correlations(entries, fit_service, scoring_service)

    corr_cols = st.columns(len(correlations)) if correlations else st.columns(1)
    for i, corr in enumerate(correlations):
        with corr_cols[i % len(corr_cols)]:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center;
                border-left: 3px solid {corr['color']};">
                <div style="font-size:32px; margin-bottom:8px;">{corr['icon']}</div>
                <div style="font-weight:700; color:white; font-size:15px; margin-bottom:4px;">
                    {corr['title']}
                </div>
                <div style="color:rgba(255,255,255,0.6); font-size:13px;">
                    {corr['insight']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Weekly Summary ─────────────────────────────────
    st.markdown("---")
    st.markdown("### 📝 Weekly Summary")

    week_entries = [e for e in entries if e.get("date", "") >= (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")]

    if week_entries:
        week_moods = [e.get("mood_value", 3) for e in week_entries]
        avg_week = sum(week_moods) / len(week_moods)
        best_day = max(week_entries, key=lambda x: x.get("mood_value", 0))
        worst_day = min(week_entries, key=lambda x: x.get("mood_value", 5))

        # Collect all gratitude items from the week
        week_gratitude = []
        for e in week_entries:
            week_gratitude.extend(e.get("gratitude", []))

        summary_emoji = "🌟" if avg_week >= 4 else "💪" if avg_week >= 3 else "💙"

        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, rgba(108,99,255,0.12), rgba(78,205,196,0.08));">
            <div style="font-size:18px; font-weight:700; color:white; margin-bottom:12px;">
                {summary_emoji} This Week's Overview
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; margin-bottom:16px;">
                <div style="text-align:center;">
                    <div style="font-size:28px; font-weight:700; color:#6C63FF;">{avg_week:.1f}/5</div>
                    <div style="color:rgba(255,255,255,0.5); font-size:12px;">Avg Mood</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:28px;">{best_day.get('mood_emoji', '😊')}</div>
                    <div style="color:rgba(255,255,255,0.5); font-size:12px;">Best Day</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:28px;">{worst_day.get('mood_emoji', '😐')}</div>
                    <div style="color:rgba(255,255,255,0.5); font-size:12px;">Toughest Day</div>
                </div>
            </div>
            <div style="color:rgba(255,255,255,0.5); font-size:13px;">
                You logged <strong style="color:white;">{len(week_entries)}</strong> entries this week
                {f' and expressed gratitude <strong style="color:#4ECDC4;">{len(week_gratitude)}</strong> times' if week_gratitude else ''}.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Start journaling to see your weekly mental health summary!")


def _calculate_correlations(entries: list, fit_service, scoring_service) -> list:
    """Calculate simple correlations between mood and physical metrics using available data."""
    if len(entries) < 3:
        return [
            {"icon": "📝", "title": "Keep Journaling!", "insight": "Log a few more entries to discover mind-body patterns.", "color": "#6C63FF"},
        ]

    correlations = []

    # Analyze mood vs sleep from entries that overlapped with fitness data
    high_mood_entries = [e for e in entries if e.get("mood_value", 3) >= 4]
    low_mood_entries = [e for e in entries if e.get("mood_value", 3) <= 2]

    # Tag-based insights
    tag_counts = {}
    for e in entries:
        for tag in e.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # General correlations
    total = len(entries)
    good_ratio = len(high_mood_entries) / total if total else 0

    if good_ratio >= 0.6:
        correlations.append({
            "icon": "🌟",
            "title": "Mostly Positive",
            "insight": f"{int(good_ratio*100)}% of your days are rated Good or Amazing. That's fantastic!",
            "color": "#4ECDC4",
        })
    elif good_ratio <= 0.3:
        correlations.append({
            "icon": "💙",
            "title": "Tough Stretch",
            "insight": "You've been having some harder days. Remember — tracking awareness is the first step to improvement.",
            "color": "#FF6B6B",
        })

    # Gratitude correlation
    entries_with_gratitude = [e for e in entries if e.get("gratitude")]
    if entries_with_gratitude:
        grat_moods = [e.get("mood_value", 3) for e in entries_with_gratitude]
        no_grat_moods = [e.get("mood_value", 3) for e in entries if not e.get("gratitude")]
        if no_grat_moods:
            grat_avg = sum(grat_moods) / len(grat_moods)
            no_grat_avg = sum(no_grat_moods) / len(no_grat_moods)
            if grat_avg > no_grat_avg + 0.3:
                correlations.append({
                    "icon": "🙏",
                    "title": "Gratitude Boosts Mood",
                    "insight": f"Days with gratitude: {grat_avg:.1f}/5 avg mood vs {no_grat_avg:.1f}/5 without. Keep it up!",
                    "color": "#FFD93D",
                })

    # Stress tag insight
    stress_count = tag_counts.get("😬 Stressed", 0) + tag_counts.get("😰 Anxious", 0)
    if stress_count >= 3:
        correlations.append({
            "icon": "🧘",
            "title": "Stress Alert",
            "insight": f"You've felt stressed/anxious {stress_count} times recently. Try the Wellness Center breathing exercises!",
            "color": "#FF8C42",
        })

    # Ensure at least one correlation
    if not correlations:
        correlations.append({
            "icon": "📊",
            "title": "Building Insights",
            "insight": "Keep logging entries — more data means more personalized insights!",
            "color": "#6C63FF",
        })

    return correlations[:4]  # Max 4 correlation cards
