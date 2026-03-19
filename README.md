# 💙 DayScore — Smart Wellness Tracking App

A modern, production-ready wellness web application that connects to Google Fit,
calculates a daily health score (0–100), provides insights, motivation, and
relaxation tools, and encourages healthy habits through gamification.

![DayScore](https://img.shields.io/badge/DayScore-v1.0.0-6C63FF?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-4ECDC4?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41-FF6B6B?style=for-the-badge)
![Firebase](https://img.shields.io/badge/Firebase-Firestore-FFD93D?style=for-the-badge)

---

## ✨ Features

### 📊 Dashboard
- Circular DayScore gauge (0-100)
- Real-time fitness metrics (steps, sleep, calories, heart rate)
- Weekly trend charts
- Motivational messages
- Personalized suggestions

### 🏆 Achievements
- 10 unlockable badges
- Progress tracking
- Category-based organization

### 📈 Results & Insights
- Best/average/worst score analytics
- Weekly trend analysis
- Detailed metric breakdowns (steps, sleep, calories)
- Improvement suggestions

### 👥 Community Challenges
- Create and join team challenges
- Global leaderboard
- Multiple metric targets

### 🧘 Wellness Center
- **Breathing Exercises** — 4-4-6, 4-7-8, Box Breathing patterns with animated circle
- **Games** — Reaction time, memory sequence, number zen
- **Relaxing Sounds** — Rain, forest, white noise, 432Hz, 528Hz tones

### 🤖 AI Wellness Coach
- Workout suggestions
- Sleep & nutrition tips
- Stress management
- OpenAI-powered (with rule-based fallback)

### 🔔 Smart Notifications
- Low score alerts
- Walk, water, sleep reminders

---

## 🗂️ Project Structure

```
dayscore-full/
├── app.py                      # Main entry point
├── requirements.txt            # Dependencies
├── .env.example                # Environment variables template
├── .gitignore
├── .streamlit/
│   └── config.toml             # Streamlit theme & settings
├── config/
│   ├── __init__.py
│   ├── settings.py             # Central configuration
│   └── firebase_config.py      # Firebase initialization
├── auth/
│   ├── __init__.py
│   └── auth_service.py         # Authentication logic
├── services/
│   ├── __init__.py
│   ├── scoring_service.py      # DayScore calculation engine
│   ├── google_fit_service.py   # Google Fit API integration
│   ├── achievement_service.py  # Achievement system
│   ├── challenge_service.py    # Community challenges
│   ├── chatbot_service.py      # AI chatbot
│   ├── notification_service.py # Reminders & alerts
│   └── streak_service.py       # Streak tracking
├── features/
│   ├── __init__.py
│   ├── dashboard.py            # Dashboard page
│   ├── results.py              # Results & Insights page
│   ├── achievements.py         # Achievements page
│   ├── challenges.py           # Community Challenges page
│   ├── wellness.py             # Wellness Center page
│   ├── chatbot.py              # AI Coach page
│   └── settings.py             # Settings page
└── utils/
    ├── __init__.py
    ├── ui_components.py        # Reusable UI components & CSS
    └── helpers.py              # Utility functions
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/dayscore.git
cd dayscore

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your credentials
```

### 3. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

> **💡 Demo Mode:** You can try the app without any API keys!
> Click "Try Demo Mode" on the login page to use simulated data.

---

## 🔧 Setup Guides

### Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project (e.g., "DayScore")
3. Enable **Authentication** → Sign-in method → Email/Password
4. Create a **Firestore Database** (start in test mode)
5. Go to Project Settings → Service Accounts → Generate new private key
6. Save the JSON file as `config/serviceAccountKey.json`
7. Copy the Firebase config values to your `.env` file

#### Firestore Collections (auto-created)
| Collection | Description |
|---|---|
| `users` | User profiles, streaks, points |
| `daily_scores` | Daily score history |
| `challenges` | Community challenges |
| `leaderboard` | Challenge rankings |
| `achievements` | Unlocked achievements |
| `chat_history` | AI chat logs |

### Google Fit OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project or select existing
3. Enable **Fitness API**
4. Go to **Credentials** → Create OAuth 2.0 Client ID
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8501`
5. Copy Client ID and Client Secret to `.env`

### OpenAI Setup (Optional)

1. Get an API key from [OpenAI](https://platform.openai.com/)
2. Add `OPENAI_API_KEY` to your `.env` file
3. The chatbot uses GPT-3.5-turbo by default

> **Note:** The chatbot works without OpenAI using intelligent rule-based responses!

---

## 📊 DayScore Formula

| Metric | Weight | Ideal | Scoring |
|---|---|---|---|
| Steps | 30% | 10,000 | Linear (0-100% of ideal) |
| Sleep | 30% | 7-8 hours | Peak at 7-8h, tapers outside |
| Calories | 20% | 2,000 | Linear (0-100% of ideal) |
| Heart Rate | 20% | 60-100 BPM | Best at lower normal range |

**Final Score** = Σ (component_score × weight), capped at 0-100.

---

## 🏅 Achievements

| Badge | Name | Condition |
|---|---|---|
| 🎉 | Welcome Aboard | First login |
| 🏃 | Marathon Walker | 10,000 steps in a day |
| 🦶 | Ultra Walker | 20,000 steps in a day |
| 🔥 | Week Warrior | 7-day streak |
| 🏆 | Monthly Maestro | 30-day streak |
| ⭐ | High Achiever | Score 80+ |
| 🌟 | Health Master | Score 90+ |
| 💯 | Perfect Day | Score 100 |
| 😴 | Sleep Champion | 5 days of 7-8h sleep |
| 👑 | Calorie King | Burn 2,500+ calories |

---

## ☁️ Deployment (Streamlit Cloud)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub repo
4. Set the main file path to `app.py`
5. Add environment variables in **Secrets**:

```toml
# .streamlit/secrets.toml format
FIREBASE_API_KEY = "your_key"
FIREBASE_AUTH_DOMAIN = "your_project.firebaseapp.com"
FIREBASE_PROJECT_ID = "your_project_id"
# ... (all .env variables)
```

6. Deploy! 🚀

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit, Plotly, Custom CSS |
| Backend | Firebase (Auth + Firestore) |
| Health Data | Google Fit API (OAuth 2.0) |
| AI | OpenAI GPT-3.5-turbo |
| Charts | Plotly.js |
| Styling | Custom CSS with glassmorphism |

---

## 📝 License

MIT License — feel free to use and modify!

---

<div align="center">

**Built with ❤️ by DayScore Team**

💙 Track • 📊 Score • 🏆 Achieve • 🧘 Relax

</div>
