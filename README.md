# 🏆 CIT Coders Arena & Departmental Battleground

A modern, high-performance web dashboard showcasing coding metrics across all **8 departments** of the Chennai Institute of Technology. It tracks and compares coding profiles from **LeetCode**, **Codeforces**, **CodeChef**, and **GitHub** for over 1,780 active students.

---

## ✨ Features

- **📊 Departmental Battleground**: Live comparison of average coding ratings across departments (AIDS, AIML, CS, CSBS, CSE, ECE, IT, VLSI).
- **⚔️ Code Duel Arena**: Pit two CIT coders side-by-side to compare ratings, problems solved, and GitHub repo count in real-time.
- **🛡️ Custom Shoutout Cards**: Generate and download verified achievement certificates (Guardian/Knight/Specialist) as customizable posters.
- **💻 Terminal Profile Scanner**: Initiates a mock "hacking scan" of any student's coding metrics with a retro terminal interface.
- **🔍 Global Search & Filter**: Search student profiles by name, department, or handles.

---

## ⚙️ Alignment & Realignment Engine

Roster PDFs often suffer from rendering drifts and localized copy-paste swaps. To solve this, this repository contains a state-of-the-art **hybrid alignment engine**:

1. **Viterbi Dynamic Programming (Phase 1)**: Formulates class-wide page-boundary rendering shifts as a Viterbi path alignment problem with states `{-1, 0, +1}`. Successfully corrects multi-row rendering displacements.
2. **Self-Healing Swap Matcher (Phase 2)**: Re-evaluates local swaps in a ±5 row window using a one-to-one mapping pool to heal localized swaps without introducing duplicates.
3. **Substring Extension Guard**: Tightens matching heuristics by checking if trailing handle characters constitute an extended name, resolving name collisions (e.g. distinguishing `Vignesh` from `Vigneshwar`).

---

## 🚀 Setup & Execution

### Prerequisites

- Python 3.10+
- `pypdf` library (for roster parsing)
- `requests` library (for API queries)

### 1. Parse & Scan Profiles
To parse the student roster PDF, align columns, and fetch real-time ratings from LeetCode, Codeforces, and GitHub:
```bash
python scan_entire_college.py
```

### 2. Verify Alignment
To run the automated verification suite against original PDF lines:
```bash
python cross_check.py
```

### 3. Run Web Dashboard
Start a local HTTP server to run the frontend dashboard:
```bash
python -m http.server 8000
```
Then visit **[http://localhost:8000](http://localhost:8000)** in your browser.

---

## 📂 File Architecture

- `scan_entire_college.py` - Core parsing, DP realignment, and batch API data scraper.
- `cross_check.py` - Validator checking the database against raw PDF coordinates.
- `index.html` - Premium glassmorphic glass-UI dashboard.
- `app.js` - Dashboard logic, Code Duel engine, and certificate generator.
- `style.css` - Custom styling tokens, vibrant glows, and responsive styling.
- `data.js` - Database compiled from student scraper.
- `knights.json` - Raw database export of all 1,782 student profiles.
