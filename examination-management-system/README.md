# Task 5: Online Examination System

A full-stack web platform for conducting online examinations, built with Python (`sqlite3` + REST API) and a dynamic HTML/CSS/JS frontend.

## Key Features
- **User Authentication (`auth.py`)**: Student registration and login with salted SHA-256 password hashing and session tokens.
- **REST API Integration (`server.py`, `exams.py`)**: JSON endpoints (`/api/exams`, `/api/exams/<id>`, `/api/submit`, `/api/results`) serving dynamic exam catalogs and grading.
- **Dynamic Exam Runner (`index.html`)**: Live countdown timer, dynamic card rendering, and instant result history.
- **Search & Filtering**: Real-time keyword search plus category and difficulty filters.
- **Performance Optimization**: SQLite indexes, backend query caching, and debounced frontend search inputs.

## How to Run
1. Run unit tests: `python3 -m unittest test_exams.py`
2. Start the web server: `python3 server.py`
3. Open `http://127.0.0.1:8000` in your browser.