import sqlite3

# Keep the database filename in one place so tests can swap it easily
DB_FILE = "inventory.db"


def connect_db():
    """Opens a connection to SQLite and lets us access columns by name."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    """Creates the products table on first run if it doesn't exist yet."""
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity >= 0),
                reorder_level INTEGER NOT NULL DEFAULT 5,
                unit_price REAL NOT NULL CHECK(unit_price >= 0)
            )
        """)
        