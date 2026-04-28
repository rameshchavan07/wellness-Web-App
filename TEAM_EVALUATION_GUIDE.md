# DayScore - Team Evaluation & Technical Contribution Guide

This document breaks down the DayScore project into 4 distinct technical roles. It details exactly what each person built, the technologies they used, and potential technical questions an evaluator (professor/interviewer) might ask, along with the ideal answers.

---

## 👤 Person 1: Frontend & UI/UX Developer

### What They Built
Designed and developed the entire user interface using Streamlit. They transformed a basic data-science framework into a premium, responsive mobile-first web application. They handled the visual routing, the floating chat interfaces, and the interactive health dashboards.

### Key Technologies Used
* **Streamlit** (Python frontend framework)
* **HTML5 & CSS3** (Injected for custom styling)
* **Session State Management** (To maintain UI state between page reloads)

### Evaluator Questions & Answers

**Q1: Streamlit is known for being very basic and blocky. How did you achieve this modern, customized UI?**
> **Answer:** "Streamlit natively lacks deep customization, so I used `st.markdown(unsafe_allow_html=True)` to inject raw CSS and HTML. This allowed me to create glassmorphism effects, gradient typography, custom rounded containers, and a floating chat window. I also used `st.columns` to build responsive, grid-like layouts that look great on both desktop and mobile."

**Q2: How do you handle navigation between pages without the user losing their data?**
> **Answer:** "I utilized Streamlit's `st.navigation` and `st.Page` API. To prevent data loss during navigation, I relied heavily on Streamlit's `st.session_state`. Any data the user enters or fetches (like their DayScore or journal entries) is cached in the session state so that when they switch pages, the UI reads from the cache instead of making a new database request."

**Q3: How did you implement the Floating AI Chat UI?**
> **Answer:** "I used custom CSS with `position: fixed` to pin the chat icon to the bottom right of the screen. When the user clicks it, it triggers a state change in Python that renders a pop-up container over the main content using z-index layering."

---

## 👤 Person 2: Backend & Database Architect

### What They Built
Engineered the cloud database infrastructure. They designed the NoSQL data schemas, handled data persistence for user health metrics, streaks, and journal entries, and ensured database queries were optimized for speed.

### Key Technologies Used
* **Firebase Firestore** (NoSQL Database)
* **Firebase Admin SDK** (Server-side database operations)
* **Python (Data Structures & Dictionaries)**

### Evaluator Questions & Answers

**Q1: Why did you choose Firestore over a relational database like SQL or PostgreSQL?**
> **Answer:** "Firestore is a NoSQL document database, which is highly scalable and schema-less. Since our app deals with rapid, unstructured data like daily journal entries, chat histories, and varying health metrics, NoSQL allows us to easily add new features without running complex database migrations. It also provides blazing-fast read times for the dashboard."

**Q2: How did you structure the collections to ensure data is fetched efficiently?**
> **Answer:** "I kept the data normalized to prevent massive document sizes. We have root collections like `users`, `counselors`, and `counselor_bookings`. The `users` collection stores basic profiles and summary stats (like total points and streaks). Heavier data, like appointments, are kept in separate collections and queried using the user's UID to keep the initial login fetch incredibly fast."

**Q3: How do you prevent database connection timeouts or memory leaks?**
> **Answer:** "I implemented a Singleton pattern using Streamlit's `@st.cache_resource`. This ensures that the Firebase Admin SDK and Firestore client are only initialized exactly once when the server boots up, rather than establishing a new connection every time a user clicks a button."

---

## 👤 Person 3: Authentication, Security & Role Management

### What They Built
Built the security layer of the application. They integrated Google OAuth, handled email/password encryption, and built the Role-Based Access Control (RBAC) system. They also automated the onboarding process for medical professionals.

### Key Technologies Used
* **Firebase Authentication** (OAuth & Credential Management)
* **Python smtplib & email.message** (Automated Email Dispatch)
* **Jitsi API / UUID** (Meeting Link Generation)

### Evaluator Questions & Answers

**Q1: How exactly does your authentication system verify users securely?**
> **Answer:** "We use Firebase Authentication. I send the user's email and password to the Firebase REST API, which securely hashes the password and returns a JWT (JSON Web Token) and a unique UID. We never store raw passwords in our own database. For Google Sign-In, we use OAuth 2.0 to verify the user's Google credentials before granting access."

**Q2: Since your app has both Patients and Counselors, how do you prevent a Patient from accessing the Counselor Dashboard?**
> **Answer:** "I implemented Role-Based Access Control (RBAC). When an account is created, I store a `role` field in their Firestore document (either 'patient' or 'counselor'). On login, the backend fetches this document and saves the role to the session state. The frontend navigation logic acts as a middleware; it checks this role and explicitly hides the patient views from counselors and vice-versa."

**Q3: How did you automate the registration of new counselors?**
> **Answer:** "I built a standalone Python backend script. It loops through a list of professional emails, uses the Firebase Admin SDK to bypass the frontend and create accounts, and saves their specific specialties to the database. It then generates a unique Jitsi video-call link using Python's `uuid` library, and uses `smtplib` to securely connect to an SMTP server and email them their credentials and meeting link."

---

## 👤 Person 4: Core Logic, AI & Third-Party Integrations

### What They Built
Developed the "brain" of the application. They integrated the Google Fit API to fetch live health data, built the algorithm that calculates the "DayScore," and integrated the OpenAI API to power the therapeutic AI chatbot.

### Key Technologies Used
* **Google Fit REST API & OAuth 2.0**
* **OpenAI API (GPT Models)**
* **Python (Algorithm Design & Data Normalization)**

### Evaluator Questions & Answers

**Q1: How does the AI Counselor (Dr. Mira) provide safe advice without hallucinating medical facts?**
> **Answer:** "I integrated the OpenAI API and engineered a highly restrictive 'System Prompt'. I explicitly instructed the model to use Cognitive Behavioral Therapy (CBT) techniques, reflect on emotions, and absolutely refrain from diagnosing conditions or prescribing medication. If a user expresses severe crisis, the prompt forces the AI to recommend emergency services."

**Q2: How do you make the AI responses personalized to the specific user?**
> **Answer:** "Before sending the user's message to OpenAI, my code fetches their current 'DayScore', their recent mood trends, and their journal streaks from the database. I dynamically inject this context into the background prompt. This way, the AI knows if the user has been sleeping poorly or tracking high anxiety before it even responds."

**Q3: The 'DayScore' is the core feature of the app. How exactly is it calculated?**
> **Answer:** "I use the Google Fit API to fetch raw daily metrics (steps, sleep, calories, heart rate). I built a `ScoringConfig` algorithm that normalizes these values against healthy ideals (e.g., 10,000 steps = 100%). I then apply a weighted average—giving 30% weight to sleep, 30% to steps, and 20% to calories and heart rate. This raw math is then converted into a clean score out of 100."
