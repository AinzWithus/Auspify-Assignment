import sqlite3
from datetime import date
from database import get_db

# Simple in-memory cache for department lookups to avoid repeated DB queries
_department_cache = {}


def clear_cache():
    """Clears the department cache whenever departments are added or modified."""
    _department_cache.clear()


def add_department(name, manager_name="Unassigned"):
    """Creates a new department."""
    clean_name = name.strip()
    if not clean_name:
        return False, "Department name cannot be empty."

    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO departments (name, manager_name) VALUES (?, ?)",
                (clean_name, manager_name.strip() or "Unassigned"),
            )
        clear_cache()
        return True, f"Department '{clean_name}' created."
    except sqlite3.IntegrityError:
        return False, f"Department '{clean_name}' already exists."


def list_departments():
    """Returns all departments, using memory cache when available."""
    if "all" in _department_cache:
        return _department_cache["all"]

    with get_db() as conn:
        rows = conn.execute("SELECT * FROM departments ORDER BY name ASC").fetchall()
        _department_cache["all"] = rows
        return rows


def register_employee(emp_code, full_name, email, role, salary, department_id=None, hire_date=None):
    """Registers a new employee record after basic validation."""
    code = emp_code.strip().upper()
    name = full_name.strip()
    clean_email = email.strip().lower()
    clean_role = role.strip()

    if not code or not name or "@" not in clean_email:
        return False, "Please provide a valid employee code, name, and email address."

    if salary < 0:
        return False, "Salary cannot be negative."

    # Default hire date to today if the user leaves it blank
    assigned_date = hire_date.strip() if hire_date and hire_date.strip() else str(date.today())

    try:
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO employees (emp_code, full_name, email, role, salary, department_id, hire_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (code, name, clean_email, clean_role, salary, department_id, assigned_date),
            )
        return True, f"Employee '{name}' ({code}) registered successfully."
    except sqlite3.IntegrityError as err:
        if "emp_code" in str(err):
            return False, f"Employee code '{code}' is already taken."
        if "email" in str(err):
            return False, f"Email '{clean_email}' is already registered."
        return False, "Could not save employee due to a database constraint (check department ID)."


def update_employee(emp_code, role=None, salary=None, department_id=None, status=None):
    """Updates specific fields for an existing employee without overwriting untouched ones."""
    code = emp_code.strip().upper()

    with get_db() as conn:
        existing = conn.execute("SELECT * FROM employees WHERE emp_code = ?", (code,)).fetchone()
        if not existing:
            return False, f"No employee found with code '{code}'."

        # Keep existing values if new ones weren't provided
        new_role = role.strip() if role and role.strip() else existing["role"]
        new_salary = salary if salary is not None else existing["salary"]
        new_dept = department_id if department_id is not None else existing["department_id"]
        new_status = status.strip() if status and status.strip() else existing["status"]

        if new_salary < 0:
            return False, "Salary cannot be negative."

        conn.execute(
            """
            UPDATE employees
            SET role = ?, salary = ?, department_id = ?, status = ?
            WHERE emp_code = ?
            """,
            (new_role, new_salary, new_dept, new_status, code),
        )
        return True, f"Updated record for {existing['full_name']} ({code})."


def delete_employee(emp_code):
    """Removes an employee record from the system."""
    code = emp_code.strip().upper()
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM employees WHERE emp_code = ?", (code,))
        if cursor.rowcount == 0:
            return False, f"Employee '{code}' not found."
        return True, f"Employee '{code}' deleted."


def search_employees(keyword="", department_name=""):
    """Searches employees by name, code, or role, with optional department filtering."""
    query = """
        SELECT e.*, COALESCE(d.name, 'Unassigned') AS department_name
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE 1=1
    """
    params = []

    if keyword.strip():
        query += " AND (e.full_name LIKE ? OR e.emp_code LIKE ? OR e.role LIKE ?)"
        like_term = f"%{keyword.strip()}%"
        params.extend([like_term, like_term, like_term])

    if department_name.strip():
        query += " AND LOWER(d.name) = LOWER(?)"
        params.append(department_name.strip())

    query += " ORDER BY e.full_name ASC"

    with get_db() as conn:
        return conn.execute(query, params).fetchall()