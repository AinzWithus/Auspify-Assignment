import sqlite3

DB_FILE = "online_exams.db"


def get_db():
    """Opens a SQLite connection with dictionary-style rows and foreign keys enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_database():
    """Creates tables, performance indexes, and seeds starter exams if empty."""
    with get_db() as conn:
        # Step 1: Users table for authentication
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL
            )
        """)

        # Step 2 & 3: Exams catalog table (supports listing, details, search & filtering)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                duration_mins INTEGER NOT NULL,
                description TEXT NOT NULL
            )
        """)

        # Questions linked to each exam
        conn.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER NOT NULL,
                prompt TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_option TEXT NOT NULL,
                FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
            )
        """)

        # Student submission history
        conn.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                exam_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (exam_id) REFERENCES exams(id)
            )
        """)

        # Step 5: Indexes to keep search and category filtering fast
        conn.execute("CREATE INDEX IF NOT EXISTS idx_exams_category ON exams(category);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_exams_title ON exams(title);")

        # Seed realistic sample exams on first run so the API immediately has data
        count = conn.execute("SELECT COUNT(*) AS total FROM exams").fetchone()["total"]
        if count == 0:
            _seed_sample_exams(conn)


def _seed_sample_exams(conn):
    """Populates starter exams and questions so users can test immediately."""
    sample_exams = [
        (
            "PY-101",
            "Python Fundamentals Assessment",
            "Programming",
            "Beginner",
            15,
            "Covers core Python syntax, data structures, functions, and file handling.",
            [
                ("Which data type is immutable in Python?", "List", "Dictionary", "Tuple", "Set", "C"),
                ("What keyword defines a function in Python?", "func", "define", "def", "lambda", "C"),
                ("Which method adds an item to the end of a list?", "append()", "push()", "insert()", "add()", "A"),
            ],
        ),
        (
            "DB-201",
            "SQL & Relational Databases",
            "Databases",
            "Intermediate",
            20,
            "Tests SQL queries, joins, primary/foreign keys, and indexing strategies.",
            [
                ("Which SQL clause filters aggregated groups?", "WHERE", "HAVING", "ORDER BY", "GROUP BY", "B"),
                ("What does a database index primarily improve?", "Write speed", "Read/Search speed", "Disk encryption", "Network latency", "B"),
                ("Which key uniquely identifies each row in a table?", "Foreign Key", "Composite Index", "Primary Key", "Candidate Alias", "C"),
            ],
        ),
        (
            "WEB-301",
            "REST APIs & Web Architecture",
            "Web Development",
            "Advanced",
            25,
            "Evaluates HTTP status codes, stateless authentication, JSON payloads, and caching.",
            [
                ("Which HTTP status code indicates a resource was successfully created?", "200 OK", "201 Created", "204 No Content", "400 Bad Request", "B"),
                ("Which HTTP method is typically idempotent for updating a resource?", "POST", "PUT", "CONNECT", "PATCH", "B"),
                ("Why is debouncing used on search inputs in a UI?", "Encrypt passwords", "Reduce redundant API calls", "Sort database tables", "Compress CSS files", "B"),
            ],
        ),
    ]

    for code, title, category, difficulty, mins, desc, qs in sample_exams:
        cur = conn.execute(
            """
            INSERT INTO exams (code, title, category, difficulty, duration_mins, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (code, title, category, difficulty, mins, desc),
        )
        exam_id = cur.lastrowid
        for prompt, a, b, c, d, ans in qs:
            conn.execute(
                """
                INSERT INTO questions (exam_id, prompt, option_a, option_b, option_c, option_d, correct_option)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (exam_id, prompt, a, b, c, d, ans),
            )