"""
DayScore - Helper Utilities
Common utility functions used across the app.
"""

from datetime import datetime, timedelta
import random


def get_greeting() -> str:
    """Return a time-based greeting."""
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    elif hour < 21:
        return "Good evening"
    else:
        return "Good night"


def format_number(num: int) -> str:
    """Format number with commas: 12345 → '12,345'."""
    return f"{num:,}"


def get_day_labels(days: int = 7) -> list:
    """Get day labels for the past N days."""
    labels = []
    for i in range(days - 1, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        labels.append(day.strftime("%a"))
    return labels


def get_date_labels(days: int = 7) -> list:
    """Get date labels for the past N days."""
    labels = []
    for i in range(days - 1, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        labels.append(day.strftime("%b %d"))
    return labels


def get_personalized_suggestions(breakdown: dict) -> list:
    """Generate personalized improvement suggestions from score breakdown."""
    suggestions = []

    if breakdown.get("sleep", {}).get("score", 100) < 70:
        suggestions.append({
            "icon": "😴",
            "title": "Improve Sleep",
            "tip": "Try going to bed 30 minutes earlier tonight. Avoid screens 1 hour before bed.",
        })

    if breakdown.get("steps", {}).get("score", 100) < 70:
        suggestions.append({
            "icon": "🚶",
            "title": "Increase Steps",
            "tip": "Take a 15-minute walk after lunch. Park farther, take stairs!",
        })

    if breakdown.get("calories", {}).get("score", 100) < 60:
        suggestions.append({
            "icon": "🔥",
            "title": "Boost Activity",
            "tip": "Add a 20-minute workout or brisk walk to your routine.",
        })

    if breakdown.get("heart_rate", {}).get("score", 100) < 60:
        suggestions.append({
            "icon": "❤️",
            "title": "Heart Health",
            "tip": "Try deep breathing or meditation. Regular cardio helps too!",
        })

    if not suggestions:
        suggestions.append({
            "icon": "🌟",
            "title": "You're doing great!",
            "tip": "Keep up the amazing work. Consistency is key to lasting health!",
        })

    return suggestions


def generate_weekly_demo_scores() -> list:
    """Generate realistic demo weekly scores."""
    base = random.randint(55, 75)
    scores = []
    for i in range(7):
        variation = random.uniform(-15, 15)
        score = max(20, min(100, base + variation))
        scores.append(round(score, 1))
    return scores


def calculate_stats(scores: list) -> dict:
    """Calculate statistics from a list of scores."""
    if not scores:
        return {"best": 0, "average": 0, "worst": 0, "trend": "stable"}

    avg = sum(scores) / len(scores)
    best = max(scores)
    worst = min(scores)

    # Trend: compare last 3 days to the rest
    if len(scores) >= 4:
        recent = sum(scores[-3:]) / 3
        earlier = sum(scores[:-3]) / len(scores[:-3])
        if recent > earlier + 5:
            trend = "improving"
        elif recent < earlier - 5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"

    return {
        "best": round(best, 1),
        "average": round(avg, 1),
        "worst": round(worst, 1),
        "trend": trend,
    }
