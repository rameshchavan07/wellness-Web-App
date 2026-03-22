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


import io
import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

@st.cache_resource
def _get_scorecard_font(size: int):
    """Fetch Roboto font from Google Fonts for premium look."""
    try:
        url = "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf"
        r = requests.get(url, timeout=5)
        return ImageFont.truetype(io.BytesIO(r.content), size=size)
    except Exception:
        try:
            return ImageFont.truetype("arial.ttf", size=size)
        except Exception:
            return ImageFont.load_default()

def generate_scorecard_image(user_name: str, score: int, steps: int, sleep: float) -> io.BytesIO:
    """Generates a beautiful 1080x1080 image scorecard for Instagram."""
    # Create base image
    img = Image.new('RGBA', (1080, 1080), color=(15, 17, 26, 255))
    
    # Background accents
    overlay = Image.new('RGBA', (1080, 1080), color=(0,0,0,0))
    draw_overlay = ImageDraw.Draw(overlay)
    draw_overlay.ellipse((-200, -200, 500, 500), fill=(108, 99, 255, 60))
    draw_overlay.ellipse((600, 600, 1300, 1300), fill=(78, 205, 196, 60))
    img = Image.alpha_composite(img, overlay)
    
    # Drawing text
    draw = ImageDraw.Draw(img)
    font_huge = _get_scorecard_font(250)
    font_large = _get_scorecard_font(100)
    font_medium = _get_scorecard_font(60)
    font_small = _get_scorecard_font(40)
    
    # Title
    draw.text((540, 200), f"DayScore", font=font_large, fill=(108, 99, 255, 255), anchor="mm")
    draw.text((540, 300), f"{user_name}'s Daily Health", font=font_small, fill=(200, 200, 200, 255), anchor="mm")
    
    # The Score
    try:
        display_score = int(round(float(score)))
    except Exception:
        display_score = score
        
    draw.text((540, 550), f"{display_score}", font=font_huge, fill=(78, 205, 196, 255), anchor="mm")
    draw.text((540, 720), "out of 100", font=font_medium, fill=(120, 120, 120, 255), anchor="mm")
    
    # Metrics
    # Removed emojis since PIL does not support them natively and they render as missing boxes
    draw.text((300, 880), f"{steps:,}", font=font_medium, fill=(255, 255, 255, 255), anchor="mm")
    draw.text((300, 950), "STEPS", font=font_small, fill=(120, 120, 120, 255), anchor="mm")
    
    draw.text((780, 880), f"{sleep}h", font=font_medium, fill=(255, 255, 255, 255), anchor="mm")
    draw.text((780, 950), "SLEEP", font=font_small, fill=(120, 120, 120, 255), anchor="mm")
    
    # Footer
    draw.text((540, 1040), "Track yours at dayscore.app", font=_get_scorecard_font(30), fill=(100, 100, 100, 255), anchor="mm")
    
    # Convert RGBA to RGB for JPEG sharing or keep as PNG
    img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
