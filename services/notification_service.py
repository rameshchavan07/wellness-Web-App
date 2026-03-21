"""
DayScore - Notification Service
Manages health reminders and alerts.
"""

import streamlit as st
from datetime import datetime


class NotificationService:
    """Manages in-app notifications and reminders."""

    # Reminder definitions
    REMINDERS = {
        "walk": {
            "icon": "🚶",
            "title": "Time to Walk!",
            "message": "You haven't hit your step goal yet. A 15-minute walk can boost your mood and energy!",
            "condition": lambda data: data.get("steps", 0) < 5000,
        },
        "water": {
            "icon": "💧",
            "title": "Stay Hydrated!",
            "message": "Have you had enough water today? Aim for 8 glasses to stay sharp and energized.",
            "condition": lambda data: True,  # Always remind about water
        },
        "sleep": {
            "icon": "🌙",
            "title": "Bedtime Reminder",
            "message": "Consider winding down soon. Good sleep is the foundation of a great DayScore!",
            "condition": lambda data: datetime.now().hour >= 21,
        },
        "stretch": {
            "icon": "🧘",
            "title": "Stretch Break!",
            "message": "Take 2 minutes to stretch. Your body will thank you!",
            "condition": lambda data: True,
        },
    }

    def get_active_notifications(self, fitness_data: dict, score: float) -> list:
        """Get all relevant notifications for current state."""
        notifications = []

        # Low score alert
        if score < 50:
            notifications.append({
                "type": "alert",
                "icon": "⚠️",
                "title": "Low DayScore Alert",
                "message": f"Your score is {score}. Try adding a walk, improving sleep, or doing a breathing exercise!",
                "severity": "warning",
            })

        # Check conditional reminders
        for key, reminder in self.REMINDERS.items():
            try:
                if reminder["condition"](fitness_data):
                    notifications.append({
                        "type": "reminder",
                        "icon": reminder["icon"],
                        "title": reminder["title"],
                        "message": reminder["message"],
                        "severity": "info",
                    })
            except Exception:
                continue

        # Achievement-related notifications
        if score >= 80 and score < 90:
            notifications.append({
                "type": "motivation",
                "icon": "🎯",
                "title": "Almost There!",
                "message": "You're close to an A+ day! Push a little more to hit 90+.",
                "severity": "success",
            })

        return notifications

    @staticmethod
    def display_notifications(notifications: list):
        """Render notifications in the main content area (not sidebar)."""
        if not notifications:
            return

        # Show as a compact expandable section in the main area
        with st.expander("🔔 Notifications", expanded=False):
            for notif in notifications[:5]:  # Show max 5
                severity = notif.get("severity", "info")
                if severity == "warning":
                    st.warning(f"{notif['icon']} **{notif['title']}**\n\n{notif['message']}")
                elif severity == "success":
                    st.success(f"{notif['icon']} **{notif['title']}**\n\n{notif['message']}")
                else:
                    st.info(f"{notif['icon']} **{notif['title']}**\n\n{notif['message']}")
