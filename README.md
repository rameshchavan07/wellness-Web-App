# 💙 DayScore — Smart Wellness Tracking App

A modern, production-ready wellness web application that connects to Google Fit,
calculates a daily health score (0–100), provides AI-powered insights, mood journaling,
mental health tracking, counselor booking, community challenges, and gamification
to encourage healthy habits.

![DayScore](https://img.shields.io/badge/DayScore-v2.0.0-6C63FF?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12+-4ECDC4?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF6B6B?style=for-the-badge)
![Firebase](https://img.shields.io/badge/Firebase-Firestore-FFD93D?style=for-the-badge)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-412991?style=for-the-badge)

---

## ✨ Features

### 📊 Dashboard
- Circular DayScore gauge (0–100) with animated radial gradient
- Real-time fitness metrics (steps, sleep, calories, heart rate)
- 7-day weekly trend chart with sparkline
- Motivational messages & personalized suggestions
- Achievement notifications & streak tracking

### 📈 Results & Analytics
- Best / average / worst score analytics
- Weekly trend analysis with Plotly charts
- Detailed metric breakdowns (steps, sleep, calories)
- AI-powered improvement suggestions
- Exportable score history

### 🧠 Mental Health Tracker
- Mood journaling with 5-level scale (😢→😄)
- Emotion tagging (anxiety, stress, gratitude, etc.)
- Weekly mood trend charts
- Sentiment analysis on journal entries
- Mental health summary and insights

### 📝 Journal
- Daily reflective journaling with rich text
- Mood & emotion tracking per entry
- Gratitude prompts & wellness check-ins
- Historical journal browsing & search
- Firestore-backed with FieldFilter queries

### 🤖 AI Wellness Coach
- **Multi-personality chatbot** — Motivator, Therapist, Fitness Coach, Nutritionist
- OpenAI GPT-3.5-turbo powered conversations
- Intelligent rule-based fallback (works without API key)
- Conversation history stored in Firestore
- Context-aware wellness advice

### 🔮 ML Predictions
- Next-day DayScore prediction using scikit-learn
- Linear Regression model trained on user history
- Feature engineering from daily metrics
- Confidence scoring on predictions

### 👨‍⚕️ Counselor Directory
- Browse professional wellness counselors
- Filter by specialty (Anxiety, Depression, Stress, etc.)
- Book sessions with email confirmation
- Rate & review past sessions
- SMTP-powered booking notifications

### 🏆 Achievements & Gamification
- 10 unlockable achievement badges
- Streak tracking (daily, weekly, monthly)
- Points system with leveling
- Progress tracking with visual indicators
- Category-based badge organization

### 👥 Community Challenges
- Create and join team challenges
- Multiple metric targets (steps, sleep, calories)
- Global leaderboard with real-time rankings
- Challenge progress tracking
- Social motivation features

### 🧘 Wellness Center
- **Breathing Exercises** — 4-4-6, 4-7-8, Box Breathing with animated guide
- **Mind Games** — Reaction time, memory sequence, number zen
- **Relaxing Sounds** — Rain, forest, white noise, 432Hz & 528Hz tones

### 💬 User Messaging
- Real-time in-app messaging between users
- Conversation threads with timestamps
- Read receipts & message history
- Firestore-backed real-time sync

### 🔔 Smart Notifications
- Low score alerts with actionable advice
- Walk, water, and sleep reminders
- Achievement unlock celebrations
- Challenge milestone notifications

### ⚙️ Settings
- Profile management (name, avatar, bio)
- Google Fit connection & sync controls
- Theme preferences
- Notification preferences
- Account management

---

## 🗂️ Project Structure

```
dayscore-full/
├── app.py                        # Main entry point + navigation
├── requirements.txt              # Version-pinned dependencies
├── .env.example                  # Environment variables template
├── .gitignore
│
├── .streamlit/
│   └── config.toml               # Streamlit theme & settings
│
├── config/
│   ├── __init__.py
│   ├── settings.py               # Central configuration (API keys, defaults)
│   └── firebase_config.py        # Firebase Admin SDK initialization
│
├── auth/
│   ├── __init__.py
│   ├── auth_service.py           # Email/Password auth + session management
│   └── google_oauth.py           # Google OAuth 2.0 with CSRF protection
│
├── services/
│   ├── __init__.py
│   ├── scoring_service.py        # DayScore calculation engine
│   ├── google_fit_service.py     # Google Fit API (parallel fetch)
│   ├── achievement_service.py    # Badge & achievement system
│   ├── challenge_service.py      # Community challenges & leaderboard
│   ├── chatbot_service.py        # Multi-personality AI chatbot
│   ├── counselor_service.py      # Counselor directory & booking
│   ├── journal_service.py        # Mood journaling & sentiment
│   ├── messaging_service.py      # User-to-user messaging
│   ├── notification_service.py   # Smart reminders & alerts
│   ├── prediction_service.py     # ML-based score predictions
│   └── streak_service.py         # Streak calculation & tracking
│
├── features/
│   ├── __init__.py
│   ├── dashboard.py              # Dashboard page
│   ├── results.py                # Results & Analytics page
│   ├── mental_health.py          # Mental Health Tracker page
│   ├── journal.py                # Journal page
│   ├── achievements.py           # Achievements page
│   ├── challenges.py             # Community Challenges page
│   ├── wellness.py               # Wellness Center page
│   ├── chatbot.py                # AI Coach page
│   ├── counselor.py              # Counselor Directory page
│   ├── messages.py               # Messaging page
│   └── settings.py               # Settings page
│
└── utils/
    ├── __init__.py
    ├── session_manager.py        # Type-safe session state management
    ├── ui_components.py          # Reusable UI components & CSS
    └── helpers.py                # Utility functions & formatters
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ (recommended) / 3.10+ (minimum)
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
> Click **"Try Demo Mode"** on the login page to use simulated data.

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
| `chat_history` | AI chatbot conversation logs |
| `journal_entries` | Mood journal entries |
| `messages` | User-to-user messages |
| `counselor_bookings` | Counselor session bookings |

### Google Fit OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project or select existing
3. Enable **Fitness API**
4. Go to **Credentials** → Create OAuth 2.0 Client ID
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8501`
5. Copy Client ID and Client Secret to `.env`

> **🔒 Security:** OAuth flow includes CSRF token protection via `secrets.token_urlsafe()` for state parameter validation.

### OpenAI Setup (Optional)

1. Get an API key from [OpenAI](https://platform.openai.com/)
2. Add `OPENAI_API_KEY` to your `.env` file
3. The chatbot uses GPT-3.5-turbo by default

> **Note:** The chatbot works without OpenAI using intelligent rule-based responses!

### SMTP Setup (Optional — for Counselor Booking)

1. Configure SMTP settings in `.env` for booking email notifications
2. Gmail users: Use an App Password (not your account password)

---

## 📊 DayScore Formula

| Metric | Weight | Ideal | Scoring |
|---|---|---|---|
| Steps | 30% | 10,000 | Linear (0–100% of ideal) |
| Sleep | 30% | 7–8 hours | Peak at 7–8h, tapers outside |
| Calories | 20% | 2,000 | Linear (0–100% of ideal) |
| Heart Rate | 20% | 60–100 BPM | Best at lower normal range |

**Final Score** = Σ (component_score × weight), capped at 0–100.

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
| 😴 | Sleep Champion | 5 days of 7–8h sleep |
| 👑 | Calorie King | Burn 2,500+ calories |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit, Plotly, Custom CSS (Glassmorphism) |
| **Backend** | Firebase Admin SDK (Auth + Firestore) |
| **Health Data** | Google Fit API (OAuth 2.0 + CSRF protection) |
| **AI / ML** | OpenAI GPT-3.5-turbo, scikit-learn (Linear Regression) |
| **Charts** | Plotly.js (interactive, responsive) |
| **Data** | NumPy, Pandas |
| **Styling** | Custom CSS with glassmorphism, gradients, micro-animations |

---

## 📦 Dependencies (14 packages, version-pinned)

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | ≥1.40.0 | UI Framework |
| `python-dotenv` | ≥1.0.0 | Environment management |
| `firebase-admin` | ≥6.5.0 | Backend DB + Auth |
| `google-auth` | ≥2.28.0 | OAuth 2.0 |
| `google-auth-oauthlib` | ≥1.2.0 | OAuth helpers |
| `google-auth-httplib2` | ≥0.2.0 | HTTP transport |
| `google-api-python-client` | ≥2.120.0 | Google Fit API |
| `openai` | ≥1.12.0 | AI Chatbot |
| `scikit-learn` | ≥1.4.0 | ML Predictions |
| `numpy` | ≥1.26.0 | Numerical computing |
| `pandas` | ≥2.2.0 | Data processing |
| `plotly` | ≥5.18.0 | Interactive charts |
| `requests` | ≥2.31.0 | HTTP client |
| `Pillow` | ≥10.2.0 | Image processing |

---

## ⚡ Performance Optimizations

- **Parallel API calls** — Google Fit metrics fetched via `ThreadPoolExecutor` (4 threads)
- **Parallel weekly fetch** — 7 days of data loaded simultaneously
- **Caching** — `@st.cache_data(ttl=300)` for API responses
- **Singleton clients** — `@st.cache_resource` for Firebase & Auth instances
- **Native navigation** — `st.navigation` (no full page reloads)
- **FieldFilter queries** — Modern Firestore query syntax

---

## 🔒 Security

- ✅ Firebase Admin SDK (server-side authentication)
- ✅ Google OAuth 2.0 with CSRF token protection
- ✅ Service account isolation
- ✅ Secrets management via `.env` + `st.secrets`
- ✅ `.gitignore` for sensitive files
- ✅ Version-pinned dependencies
- ✅ Type-safe parameter handling
- ✅ Timezone-aware datetime (Python 3.12+ compliant)

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
GOOGLE_CLIENT_ID = "your_google_client_id"
GOOGLE_CLIENT_SECRET = "your_google_client_secret"
OPENAI_API_KEY = "your_openai_key"
```

6. Deploy! 🚀

---

## 📝 License

MIT License — feel free to use and modify!

---

<div align="center">

**Built with ❤️ by DayScore Team**

💙 Track • 📊 Score • 🧠 Reflect • 🏆 Achieve • 🧘 Relax

</div>
