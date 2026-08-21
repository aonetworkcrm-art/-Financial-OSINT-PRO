"""
🗄️ NEXUS INTEL — Database Module
SQLite para usuarios, órdenes y tokens
"""
import sqlite3
import hashlib
import os
from datetime import datetime
from pathlib import Path

DB_PATH = str(Path(__file__).parent / "nexus_intel.db")


def get_db():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicializar todas las tablas"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT DEFAULT '',
            whatsapp TEXT DEFAULT '',
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            key_token TEXT UNIQUE NOT NULL,
            plan TEXT NOT NULL,
            searches_limit INTEGER NOT NULL DEFAULT 0,
            searches_used INTEGER NOT NULL DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            plan TEXT NOT NULL,
            price REAL NOT NULL,
            searches INTEGER NOT NULL,
            payment_method TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            api_token TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            approved_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            api_key_id INTEGER,
            query_type TEXT,
            query_value TEXT,
            results_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Crear admin por defecto
    admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, ?)",
            ("admin", "admin@nexusintel.com", admin_hash, "Administrator", "admin")
        )
        print("[DB] Admin user created: admin / admin123")

    conn.commit()
    conn.close()
    print("[DB] Database initialized successfully")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username: str, email: str, password: str, full_name: str = "", whatsapp: str = "") -> dict:
    """Crear un nuevo usuario"""
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, full_name, whatsapp) VALUES (?, ?, ?, ?, ?)",
            (username, email, hash_password(password), full_name, whatsapp)
        )
        conn.commit()
        user = cursor.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return dict(user) if user else None
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def login_user(username: str, password: str) -> dict:
    """Autenticar usuario"""
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username, hash_password(password))
    ).fetchone()
    if user:
        conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.now().isoformat(), user["id"]))
        conn.commit()
    conn.close()
    return dict(user) if user else None


def get_user(user_id: int) -> dict:
    """Obtener usuario por ID"""
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_email(email: str) -> dict:
    """Obtener usuario por email"""
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(user) if user else None


def get_all_users() -> list:
    """Obtener todos los usuarios"""
    conn = get_db()
    users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(u) for u in users]


def create_order(order_id: str, user_id: int, plan: str, price: float, searches: int, payment_method: str = "") -> dict:
    """Crear una orden"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (order_id, user_id, plan, price, searches, payment_method) VALUES (?, ?, ?, ?, ?, ?)",
        (order_id, user_id, plan, price, searches, payment_method)
    )
    conn.commit()
    order = cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    conn.close()
    return dict(order) if order else None


def approve_order(order_id: str) -> dict:
    """Aprobar una orden y generar API key"""
    conn = get_db()
    order = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    if not order:
        conn.close()
        return None

    import secrets
    token = f"NEXUS-{order['plan'].upper()[:3]}-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"

    conn.execute(
        "UPDATE orders SET status = 'approved', api_token = ?, approved_at = ? WHERE order_id = ?",
        (token, datetime.now().isoformat(), order_id)
    )

    conn.execute(
        "INSERT INTO api_keys (user_id, key_token, plan, searches_limit) VALUES (?, ?, ?, ?)",
        (order["user_id"], token, order["plan"], order["searches"])
    )

    conn.commit()
    conn.close()
    return {"order_id": order_id, "api_token": token, "plan": order["plan"]}


def get_all_orders() -> list:
    """Obtener todas las órdenes"""
    conn = get_db()
    orders = conn.execute("""
        SELECT o.*, u.username, u.email 
        FROM orders o 
        LEFT JOIN users u ON o.user_id = u.id 
        ORDER BY o.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(o) for o in orders]


def get_pending_orders() -> list:
    """Obtener órdenes pendientes"""
    conn = get_db()
    orders = conn.execute("""
        SELECT o.*, u.username, u.email 
        FROM orders o 
        LEFT JOIN users u ON o.user_id = u.id 
        WHERE o.status = 'pending'
        ORDER BY o.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(o) for o in orders]


def validate_api_key(key_token: str) -> dict:
    """Validar una API key y retornar info"""
    conn = get_db()
    key = conn.execute("""
        SELECT ak.*, u.username, u.email 
        FROM api_keys ak 
        JOIN users u ON ak.user_id = u.id 
        WHERE ak.key_token = ? AND ak.status = 'active'
    """, (key_token,)).fetchone()
    conn.close()

    if not key:
        return None

    key_dict = dict(key)
    if key_dict["searches_used"] >= key_dict["searches_limit"]:
        key_dict["status"] = "exhausted"
        return key_dict

    return key_dict


def use_search_credit(api_key_id: int):
    """Descontar 1 crédito de búsqueda"""
    conn = get_db()
    conn.execute("UPDATE api_keys SET searches_used = searches_used + 1 WHERE id = ?", (api_key_id,))
    conn.commit()
    conn.close()


def log_search(user_id: int, api_key_id: int, query_type: str, query_value: str, results_count: int = 0):
    """Registrar una búsqueda"""
    conn = get_db()
    conn.execute(
        "INSERT INTO search_logs (user_id, api_key_id, query_type, query_value, results_count) VALUES (?, ?, ?, ?, ?)",
        (user_id, api_key_id, query_type, query_value, results_count)
    )
    conn.commit()
    conn.close()


def get_user_stats(user_id: int) -> dict:
    """Obtener estadísticas del usuario"""
    conn = get_db()
    keys = conn.execute("SELECT * FROM api_keys WHERE user_id = ?", (user_id,)).fetchall()
    searches = conn.execute("SELECT COUNT(*) as total FROM search_logs WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()

    total_limit = sum(k["searches_limit"] for k in keys)
    total_used = sum(k["searches_used"] for k in keys)

    return {
        "api_keys": [dict(k) for k in keys],
        "total_searches_limit": total_limit,
        "total_searches_used": total_used,
        "total_searches_remaining": total_limit - total_used,
        "total_searches": searches["total"] if searches else 0,
    }


def get_dashboard_stats() -> dict:
    """Obtener estadísticas del dashboard admin"""
    conn = get_db()
    users_count = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
    orders_count = conn.execute("SELECT COUNT(*) as c FROM orders").fetchone()["c"]
    pending_count = conn.execute("SELECT COUNT(*) as c FROM orders WHERE status = 'pending'").fetchone()["c"]
    revenue = conn.execute("SELECT COALESCE(SUM(price), 0) as r FROM orders WHERE status = 'approved'").fetchone()["r"]
    searches_total = conn.execute("SELECT COUNT(*) as c FROM search_logs").fetchone()["c"]
    conn.close()

    return {
        "total_users": users_count,
        "total_orders": orders_count,
        "pending_orders": pending_count,
        "total_revenue": revenue,
        "total_searches": searches_total,
    }
