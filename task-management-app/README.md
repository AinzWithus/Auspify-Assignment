# Task 6: Task & Deadline Management App

A secure full-stack productivity application for managing tasks, deadlines, and automated performance reports, built with Python (`sqlite3` + REST API) and a responsive web UI.

## Key Features
- **Authentication & Security (`auth.py`, `server.py`)**: Salted SHA-256 password hashing, brute-force login lockout, security headers, and strict per-user authorization isolation.
- **Task & Deadline Management (`tasks.py`)**: Input-validated task creation, priority levels (`High`, `Medium`, `Low`), deadline tracking, and overdue detection.
- **Automated Performance Reports (`reports.py`)**: Weighted productivity score calculation, completion rates, and performance grading.
- **Security & Unit Testing (`test_tasks.py`)**: Verifies cross-user authorization boundaries, input validation, and report accuracy.

## How to Run
1. Run security & unit tests: `python3 -m unittest test_tasks.py`
2. Start the server: `python3 server.py`
3. Open `http://127.0.0.1:8080` in your browser.