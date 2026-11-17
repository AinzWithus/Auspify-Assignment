import hashlib
import os
import secrets
import sqlite3
import time
from database import get_db

ACTIVE_SESSIONS = {}
FAILED_ATTEMPTS = {}  # { username: {"count": int, "locked_until": float} }
MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 60


def _hash_password(password, salt_hex):
    """Hashes a password using a unique per-user random salt and SHA-256."""
    return hashlib.sha256((salt_hex + password).encode("utf-8")).hexdigest()


def register_user(username, full_name, password):
    """Validates and registers a new user account."""
    clean_user = username.strip().lower()
    clean_name = full_name.strip()

    if len(clean_user) < 3 or not clean_user.isalnum():
        return False, "Username must be at least 3 alphanumeric characters."
    if not clean_name:
        return False, "Full name is required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    salt = os.urandom(16).hex()
    pwd_hash = _hash_password(password, salt)

    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO users (username, full_name, password_hash, salt) VALUES (?, ?, ?, ?)",
                (clean_user, clean_name, pwd_hash, salt),
            )
        return True, "Account created! Please log in."
    except sqlite3.IntegrityError:
        return False, f"Username '{clean_user}' is already taken."


def login_user(username, password):
    """Authenticates user credentials with brute-force lockout protection."""
    clean_user = username.strip().lower()
    now = time.time()

    # Check if account is temporarily locked due to repeated failed attempts
    record = FAILED_ATTEMPTS.get(clean_user)
    if record and record["locked_until"] > now:
        wait = int(record["locked_until"] - now)
        return False, f"Too many failed attempts. Try again in {wait}s.", None

    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE username = ?", (clean_user,)).fetchone()

    if not user or not secrets.compare_digest(_hash_password(password, user["salt"]), user["password_hash"]):
        attempts = (record["count"] + 1) if record else 1
        locked_until = (now + LOCKOUT_SECONDS) if attempts >= MAX_ATTEMPTS else 0
        FAILED_ATTEMPTS[clean_user] = {"count": attempts, "locked_until": locked_until}
        return False, "Invalid username or password.", None

    # Clear failed counter on valid login
    FAILED_ATTEMPTS.pop(clean_user, None)
    token = secrets.token_hex(24)
    session_data = {
        "user_id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
    }
    ACTIVE_SESSIONS[token] = session_data
    return True, f"Welcome, {user['full_name']}!", {"token": token, **session_data}


def get_session(token):
    """Looks up an active session by token."""
    if not token:
        return None
    return ACTIVE_SESSIONS.get(token.strip())


def logout_user(token):
    """Destroys an active session token."""
    ACTIVE_SESSIONS.pop(token, None)