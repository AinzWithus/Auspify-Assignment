import hashlib
import os
import secrets
import sqlite3
from database import get_db

# Active in-memory sessions: { token: {"user_id": int, "username": str, "full_name": str} }
ACTIVE_SESSIONS = {}


def _hash_password(password, salt_hex):
    """Hashes a password with a per-user random salt using SHA-256."""
    raw = (salt_hex + password).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def register_user(username, full_name, password):
    """Creates a new student account with salted password storage."""
    clean_user = username.strip().lower()
    clean_name = full_name.strip()

    if len(clean_user) < 3 or not clean_name:
        return False, "Username (min 3 chars) and full name are required."
    if len(password) < 4:
        return False, "Password must be at least 4 characters long."

    salt = os.urandom(16).hex()
    pwd_hash = _hash_password(password, salt)

    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO users (username, full_name, password_hash, salt) VALUES (?, ?, ?, ?)",
                (clean_user, clean_name, pwd_hash, salt),
            )
        return True, "Account created! You can now log in."
    except sqlite3.IntegrityError:
        return False, f"Username '{clean_user}' is already taken."


def login_user(username, password):
    """Verifies credentials and issues a session token."""
    clean_user = username.strip().lower()
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE username = ?", (clean_user,)).fetchone()

    if not user:
        return False, "Invalid username or password.", None

    expected_hash = _hash_password(password, user["salt"])
    if not secrets.compare_digest(expected_hash, user["password_hash"]):
        return False, "Invalid username or password.", None

    token = secrets.token_hex(24)
    session_data = {
        "user_id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
    }
    ACTIVE_SESSIONS[token] = session_data
    return True, f"Welcome back, {user['full_name']}!", {"token": token, **session_data}


def get_session(token):
    """Returns active user details for a valid Bearer token."""
    if not token:
        return None
    return ACTIVE_SESSIONS.get(token.strip())


def logout_user(token):
    """Invalidates an active session token."""
    ACTIVE_SESSIONS.pop(token, None)