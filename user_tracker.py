"""
User Activity Tracker — Supports Neon PostgreSQL + SQLite fallback
Used by both Streamlit tools
"""
import os
import json
import hashlib
import secrets
from datetime import datetime
from pathlib import Path

# Try PostgreSQL
try:
    import psycopg2
    import psycopg2.extras
    HAS_PG = True
except ImportError:
    HAS_PG = False

import sqlite3

# Database config
PG_URL = os.environ.get("DATABASE_URL", "")
TRACKER_DIR = Path(__file__).parent / "user_data"
SQLITE_DB = TRACKER_DIR / "tracker.db"


def _get_db():
    """Get database connection"""
    if HAS_PG and PG_URL:
        conn = psycopg2.connect(PG_URL)
        conn.autocommit = False
        return conn, "pg"
    else:
        TRACKER_DIR.mkdir(exist_ok=True)
        conn = sqlite3.connect(str(SQLITE_DB))
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"


def _close_db(conn, db_type):
    """Close connection"""
    try:
        conn.close()
    except:
        pass


def init_tracker():
    """Initialize tables"""
    conn, db_type = _get_db()
    c = conn.cursor()

    if db_type == "pg":
        c.execute("""
            CREATE TABLE IF NOT EXISTS tracker_users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(200) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name VARCHAR(200),
                role VARCHAR(20) DEFAULT 'user',
                credits INTEGER DEFAULT 0,
                plan VARCHAR(50) DEFAULT 'free',
                api_key VARCHAR(100) UNIQUE,
                total_searches INTEGER DEFAULT 0,
                total_checks INTEGER DEFAULT 0,
                total_exports INTEGER DEFAULT 0,
                total_proxies_used INTEGER DEFAULT 0,
                login_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW(),
                last_login TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS tracker_activity (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                action VARCHAR(50) NOT NULL,
                details JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
    else:
        c.execute("""
            CREATE TABLE IF NOT EXISTS tracker_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'user',
                credits INTEGER DEFAULT 0,
                plan TEXT DEFAULT 'free',
                api_key TEXT UNIQUE,
                total_searches INTEGER DEFAULT 0,
                total_checks INTEGER DEFAULT 0,
                total_exports INTEGER DEFAULT 0,
                total_proxies_used INTEGER DEFAULT 0,
                login_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS tracker_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    conn.commit()
    _close_db(conn, db_type)


def hash_password(password):
    salt = secrets.token_hex(16)
    h = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{h}"


def verify_password(password, stored):
    salt, h = stored.split(":")
    return hashlib.sha256((password + salt).encode()).hexdigest() == h


def create_tracked_user(username, email, password, full_name="", plan="free"):
    """Create user"""
    conn, db_type = _get_db()
    c = conn.cursor()
    try:
        pw_hash = hash_password(password)
        api_key = f"PCMD-{plan.upper()[:3]}-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"

        if db_type == "pg":
            c.execute("""
                INSERT INTO tracker_users (username, email, password_hash, full_name, plan, api_key)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """, (username, email, pw_hash, full_name, plan, api_key))
            user_id = c.fetchone()[0]
        else:
            c.execute("""
                INSERT INTO tracker_users (username, email, password_hash, full_name, plan, api_key)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, email, pw_hash, full_name, plan, api_key))
            user_id = c.lastrowid

        conn.commit()
        user = get_user_by_id(user_id)
        log_activity(user_id, "user_created", {"username": username, "plan": plan})
        _close_db(conn, db_type)
        return user
    except Exception as e:
        conn.rollback()
        _close_db(conn, db_type)
        return None


def authenticate_user(username_or_email, password):
    """Login"""
    conn, db_type = _get_db()
    c = conn.cursor()

    if db_type == "pg":
        c.execute("SELECT * FROM tracker_users WHERE username=%s OR email=%s", (username_or_email, username_or_email))
    else:
        c.execute("SELECT * FROM tracker_users WHERE username=? OR email=?", (username_or_email, username_or_email))

    row = c.fetchone()
    if not row:
        _close_db(conn, db_type)
        return None, None

    user = dict(row)
    if verify_password(password, user["password_hash"]):
        if db_type == "pg":
            c.execute("UPDATE tracker_users SET last_login=NOW(), login_count=login_count+1 WHERE id=%s", (user["id"],))
        else:
            c.execute("UPDATE tracker_users SET last_login=CURRENT_TIMESTAMP, login_count=login_count+1 WHERE id=?", (user["id"],))
        conn.commit()
        _close_db(conn, db_type)
        log_activity(user["id"], "login")
        return user, secrets.token_hex(16)

    _close_db(conn, db_type)
    return None, None


def get_user_by_id(user_id):
    """Get user by ID"""
    conn, db_type = _get_db()
    c = conn.cursor()
    if db_type == "pg":
        c.execute("SELECT * FROM tracker_users WHERE id=%s", (user_id,))
    else:
        c.execute("SELECT * FROM tracker_users WHERE id=?", (user_id,))
    row = c.fetchone()
    _close_db(conn, db_type)
    return dict(row) if row else None


def log_activity(user_id, action, details=None):
    """Log activity"""
    conn, db_type = _get_db()
    c = conn.cursor()
    details_str = json.dumps(details) if details else None

    if db_type == "pg":
        c.execute("INSERT INTO tracker_activity (user_id, action, details) VALUES (%s, %s, %s::jsonb)",
                  (user_id, action, details_str))
    else:
        c.execute("INSERT INTO tracker_activity (user_id, action, details) VALUES (?, ?, ?)",
                  (user_id, action, details_str))
    conn.commit()
    _close_db(conn, db_type)


def get_user_activity(user_id, limit=50):
    """Get user activity"""
    conn, db_type = _get_db()
    c = conn.cursor()
    if db_type == "pg":
        c.execute("SELECT * FROM tracker_activity WHERE user_id=%s ORDER BY created_at DESC LIMIT %s", (user_id, limit))
    else:
        c.execute("SELECT * FROM tracker_activity WHERE user_id=? ORDER BY created_at DESC LIMIT ?", (user_id, limit))
    rows = c.fetchall()
    _close_db(conn, db_type)
    return [dict(r) for r in rows]


def get_global_stats():
    """Get global stats"""
    conn, db_type = _get_db()
    c = conn.cursor()
    stats = {}
    c.execute("SELECT COUNT(*) FROM tracker_users")
    stats["total_users"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tracker_activity")
    stats["total_activities"] = c.fetchone()[0]
    _close_db(conn, db_type)
    return stats


def get_all_tracked_users():
    """Get all users"""
    conn, db_type = _get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM tracker_users ORDER BY created_at DESC")
    rows = c.fetchall()
    _close_db(conn, db_type)
    return [dict(r) for r in rows]


# Auto-init
try:
    init_tracker()
except:
    pass
