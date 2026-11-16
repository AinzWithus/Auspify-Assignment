# Task 4: Employee Management System

A modular CLI application for managing employee records, organizational departments, and payroll reports using Python and SQLite.

## Modules
- `database.py` – Relational schema (`departments` & `employees`) with foreign keys and search indexes
- `employees.py` – Department caching, employee registration, updates, deletion, and search
- `reports.py` – Organizational headcount and payroll summary reports
- `main.py` – Interactive CLI management screens
- `test_employees.py` – Unit tests covering CRUD accuracy and duplicate constraints

## How to Run
- Start the application: `python3 main.py`
- Run unit tests: `python3 -m unittest test_employees.py`