import sqlite3

# Keep the DB file path configurable so unit tests can use a separate temporary file
DB_FILE = "employees.db"


def get_db():
    """Opens a SQLite connection with dictionary-style rows and foreign keys enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    # SQLite disables foreign key checks by default; turning it on keeps data consistent
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_database():
    """Creates departments and employees tables along with search indexes."""
    with get_db() as conn:
        # Step 1: Departments table to organize company structure
        conn.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                manager_name TEXT DEFAULT 'Unassigned'
            )
        """)

        # Step 2: Employees table linked to departments
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_code TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                salary REAL NOT NULL CHECK(salary >= 0),
                department_id INTEGER,
                hire_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Active',
                FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
            )
        """)

        # Step 5 (Performance Optimization): Index frequently searched columns
        # so lookups stay fast even as the employee table grows
        conn.execute("CREATE INDEX IF NOT EXISTS idx_emp_name ON employees(full_name);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_emp_dept ON employees(department_id);")