# ⚡ QUIZ CLASH — Multiplayer Quiz Battle Game

> **"Think Fast. Answer Faster. Win the Battle."**

A complete, full-stack, real-time competitive multiplayer quiz battle web platform built with **Python (Flask)**, **Flask-SocketIO**, **SQLite**, and **JavaScript**. Designed as a college-level computer science capstone project with a dark esports theme.

---

## 🎮 Overview

**QUIZ CLASH** allows two or more players to create or join private rooms, enter a quick matchmaking queue, or practice solo. Players face identical questions simultaneously, submit answers within strict synchronized countdown timers, earn base points and speed bonuses, rack up consecutive answer streaks, and compete for victory on live leaderboards.

---

## 🛠️ Technology Stack

| Layer | Technology | Description |
|---|---|---|
| **Backend** | Python 3.10+ / Flask | Core server, application routing, REST APIs, session management |
| **Real-Time WebSockets** | Flask-SocketIO & Socket.IO v4 | Bidirectional communication for lobbies, synchronized questions & scoring |
| **Database** | SQLite + SQLAlchemy ORM | Relational persistence for users, questions, matches, stats & achievements |
| **Security** | Werkzeug Security | Salted password hashing (`generate_password_hash` / `check_password_hash`) |
| **Frontend** | HTML5, CSS3, Modern ES6+ JavaScript | Dark cyberpunk esports UI, custom grid, glassmorphism, responsive |
| **Audio Engine** | HTML5 Web Audio API | In-browser synthesized retro/arcade audio (zero missing audio file errors) |
| **Analytics & Charts** | Chart.js | Interactive win/loss doughnut charts and performance rating graphs |
| **Visuals & Icons** | Lucide Icons & Canvas Confetti | Scalable vector icons and celebratory post-victory particle explosions |

---

## 📁 Project Structure

```text
Multiplayer quiz battle game/
│
├── app.py                     # Application entry point, initializes Flask & SocketIO
├── config.py                  # App configuration, game rules constants, secret keys
├── seed_data.py               # Pre-seeds 120+ authentic questions across 8 categories
├── requirements.txt           # Python package dependencies
├── README.md                  # Comprehensive setup & presentation documentation
│
├── instance/
│   └── quiz_clash.db          # Auto-generated SQLite database
│
├── models/
│   ├── __init__.py            # SQLAlchemy db instance
│   ├── user.py                # User, PlayerStats, Achievement, UserAchievement
│   ├── question.py            # Category, Question
│   └── game.py                # MatchHistory, MatchParticipant, DailyChallengeRecord
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                # Register, Login, Logout, 1-Click Guest Mode
│   ├── main.py                # Landing page, How to Play, Tournament Rules
│   ├── dashboard.py           # Arena hub, room creation, practice, daily challenge
│   ├── leaderboard.py         # Global leaderboard & Top-3 Champions Podium
│   ├── profile.py             # User stats, Chart.js breakdown, avatar picker
│   └── admin.py               # Admin question & category management portal
│
├── game/
│   ├── __init__.py
│   ├── room_manager.py        # In-memory room states, player slots, matchmaking queue
│   ├── scoring.py             # Server-side scoring engine (base, speed bonus, streaks)
│   └── events.py              # Flask-SocketIO event handlers (lobby, battle, comms)
│
├── templates/
│   ├── base.html              # Esports master layout, audio mute toggle, flash toasts
│   ├── index.html             # Landing page with hero, live counters, PvP graphic
│   ├── login.html             # Login card + 1-Click Guest + Auto-fill Demo buttons
│   ├── register.html          # Registration card with 8 battle avatar selectors
│   ├── dashboard.html         # Arena dashboard (Quick Match, Create Room, Join Code)
│   ├── lobby.html             # Multiplayer room lobby (host controls, live chat)
│   ├── battle.html            # Real-time battle arena (PvP health bars, SVG timer ring)
│   ├── practice.html          # Solo simulation training drill with instant review
│   ├── daily_challenge.html   # Synchronized daily question set
│   ├── leaderboard.html       # Esports podium (Gold, Silver, Bronze) and rankings
│   ├── profile.html           # Player dossier with Chart.js charts & achievements
│   ├── admin.html             # Admin portal to add/edit/delete questions & categories
│   ├── how_to_play.html       # Step-by-step game guide
│   └── rules.html             # Scoring algorithms and fair-play specifications
│
├── static/
│   ├── css/
│   │   └── style.css          # Esports dark theme, neon glows, animations
│   ├── js/
│   │   ├── main.js            # Web Audio API sound generator, UI helpers
│   │   ├── lobby.js           # Lobby Socket.IO state, ready button, chat
│   │   ├── battle.js          # Live battle arena, timers, answer lock, confetti
│   │   ├── practice.js        # Solo drill engine
│   │   └── daily.js           # Daily challenge script
│   └── images/
│       └── logo.svg           # Vector crest logo for QUIZ CLASH
│
└── tests/
    ├── test_auth.py           # Unit tests for authentication, hashing, stats
    ├── test_scoring.py        # Unit tests for base points, speed bonus, streaks
    └── test_room_manager.py   # Unit tests for room lifecycle and host migration
```

---

## ⚡ Quick Start Guide

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14 installed on your machine.
- Web browser (Chrome, Edge, Firefox, or Safari).

### 2. Install Dependencies
Open your terminal inside the project directory and run:
```bash
pip install -r requirements.txt
```

### 3. Launch the Server
```bash
python app.py
```

You will see:
```text
==========================================================
  ⚡ QUIZ CLASH - MULTIPLAYER QUIZ BATTLE GAME ⚡
  Running on: http://127.0.0.1:5000
  Demo Accounts:
    - admin       / admin123  (Administrator)
    - cyber_ninja / demo123   (Player 1)
    - pixel_queen / demo123   (Player 2)
==========================================================
```

Open your browser and visit: **`http://127.0.0.1:5000`**

*(Note: On first startup, the database `quiz_clash.db` is created automatically and pre-seeded with 120 authentic questions across 8 categories, demo users, and achievements!)*

---

## 👥 Two-Player Multiplayer Demonstration Guide

To test the real-time multiplayer features on a single computer:

1. **Window 1 (Host / Player 1):**
   - Open your normal browser (e.g. Chrome) and navigate to `http://127.0.0.1:5000/login`.
   - Click the **"🥷 Cyber Ninja"** auto-fill button (or log in with `cyber_ninja` / `demo123`).
   - Click **"Configure & Create Room"** on the Dashboard.
   - Select your desired category and click **"Create Lobby"**.
   - Note the **Room Code** shown in the top right (e.g., `QC-7421`). Click the code to copy it.

2. **Window 2 (Guest / Player 2):**
   - Open a **New Incognito Window** (or another browser like Microsoft Edge) and visit `http://127.0.0.1:5000/login`.
   - Click the **"👑 Pixel Queen"** auto-fill button (or click **"Play as Guest"** for an instant guest session).
   - On the Dashboard under **"Join Room"**, paste the room code (e.g., `QC-7421`) and click **"Enter Battle Lobby"**.

3. **In the Lobby:**
   - Both players appear in the squad slots in real time.
   - Both players click the **"READY UP"** button.
   - The host clicks **"START MATCH"**.
   - A 3-second synchronized countdown appears on both screens with sound effects.

4. **In the Battle Arena:**
   - Both players receive the exact same question simultaneously.
   - Click an answer option. Once chosen, the submission is locked.
   - When both players answer (or the timer expires), the correct answer turns green, wrong choices turn red, an explanation drawer appears, and scores update live!
   - At the end of the round, the winner is announced with a confetti cannon, custom podium standings, and detailed speed/accuracy stats!

---

## 🔑 Pre-Configured Demo Accounts

| Username | Password | Role | Description |
|---|---|---|---|
| `admin` | `admin123` | **Administrator** | Access to `/admin` to add/delete questions & categories |
| `cyber_ninja` | `demo123` | **Veteran Warrior** | High-level profile with seeded match history & achievements |
| `pixel_queen` | `demo123` | **Veteran Warrior** | Second test account for quick head-to-head multiplayer |
| `neon_falcon` | `demo123` | **Warrior** | Third test account for larger lobbies |
| *Guest Mode* | *(None)* | **Guest Pass** | 1-Click instant demonstration without typing |

---

## 🧠 Scoring System & Game Mechanics

- **Base Score:** `100 points` for each correct answer.
- **Speed Bonus:** Up to `50 bonus points` awarded based on how fast the player answers:
  $$\text{Speed Bonus} = \text{round}\left( \frac{\text{Time Left}}{\text{Total Time}} \times 50 \right)$$
- **Streak Multiplier:** Consecutive correct answers build streak momentum:
  - Streak 1: `+0 bonus`
  - Streak 2: `+20 bonus`
  - Streak 3: `+40 bonus`
  - Streak 4: `+60 bonus`
  - Streak 5+: `+100 max bonus`
- **Incorrect Answer / Timeout:** `0 points` (Streak resets to 0).
- **Tie-Breaker:** When total points are tied, the player with the faster average response time takes higher rank.

---

## 🛡️ Anti-Cheating & Security Design

1. **Zero Client-Side Leakage:** Correct answers and explanations are stored strictly on the server and are only emitted over WebSockets *after* the round concludes or all players have answered.
2. **Lockout Enforcement:** The server enforces a single submission per player per round.
3. **Master Server Clock:** Question expiration and response timestamps are measured on the backend, preventing local device clock spoofing.
4. **Secure Password Hashing:** User passwords are never stored in plain text; PBKDF2/SHA256 password hashes are verified on each login.

---

## 🧪 Running Automated Unit Tests

A comprehensive unit test suite is included covering authentication, password hashing, scoring algorithms, speed bonuses, streaks, and room state management:

```bash
python -m pytest
```

Output:
```text
tests\test_auth.py ..                                                    [ 18%]
tests\test_room_manager.py ....                                          [ 54%]
tests\test_scoring.py .....                                              [100%]
====================== 11 passed in 8.58s =======================
```

---

## 🎓 College Presentation Notes

When presenting this project to professors, examiners, or classmates, highlight the following key technical achievements:

1. **Real-Time Synchronous Architecture:**
   - Explain how Flask-SocketIO manages in-memory room states and delivers questions to distributed client sessions within milliseconds.
2. **State Machine & Room Lifecycle:**
   - Discuss the lifecycle states: `waiting` (lobby) $\rightarrow$ `countdown` $\rightarrow$ `in_progress` (battle) $\rightarrow$ `intermission` $\rightarrow$ `finished` (podium).
3. **Audio Synthesis without Media Assets:**
   - Demonstrate how the Web Audio API generates procedural tones (sine, triangle, and sawtooth waves) for clicks, ticks, bells, and fanfares, ensuring 100% asset reliability.
4. **Data Visualization:**
   - Show how Chart.js renders real-time performance analytics on player profile pages.
5. **Deterministic Daily Challenge:**
   - Explain how `seed = YYYYMMDD` generates the identical question set globally for every player on a given calendar day.

---

## 🚀 Future Roadmap

- [ ] Global ranked matchmaking with ELO / MMR rating.
- [ ] Sound pack themes (Retro 8-bit, Sci-Fi Synth, Orchestral).
- [ ] Audio/voice chat integration via WebRTC mesh.
- [ ] Team 2v2 Battle Mode.
- [ ] Exportable quiz battle certificates in PDF format.
