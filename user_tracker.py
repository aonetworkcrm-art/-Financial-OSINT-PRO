"""
Proxy Commander PRO - User Activity Tracker v1.0
Tracks all user actions: logins, searches, checks, exports, favorites, payments
"""
import json
import os
import hashlib
import secrets
from datetime import datetime
from pathlib import Path
from functools import wraps

# Storage files
TRACKER_DIR = Path(__file__).parent / "user_data"
USERS_FILE = TRACKER_DIR / "users.json"
ACTIVITY_FILE = TRACKER_DIR / "activity_log.json"
SESSIONS_FILE = TRACKER_DIR / "sessions.json"
PAYMENTS_FILE = TRACKER_DIR / "payments.json"
STATS_FILE = TRACKER_DIR / "global_stats.json"


def _ensure_dir():
    """Create tracking directory if not exists"""
    TRACKER_DIR.mkdir(exist_ok=True)


def _load_json(filepath, default=None):
    """Load JSON file"""
    if default is None:
        default = {}
    if filepath.exists():
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except:
            return default
    return default


def _save_json(filepath, data):
    """Save JSON file"""
    _ensure_dir()
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


# ==================== USER MANAGEMENT ====================

def create_tracked_user(username, email, password, full_name="", whatsapp="", plan="free"):
    """Create a new tracked user with full profile"""
    _ensure_dir()
    users = _load_json(USERS_FILE, {"users": {}, "next_id": 1})

    # Check duplicate
    for uid, u in users["users"].items():
        if u["username"] == username or u["email"] == email:
            return None

    user_id = str(users["next_id"])
    users["next_id"] += 1

    # Hash password
    salt = secrets.token_hex(16)
    pw_hash = hashlib.sha256((password + salt).encode()).hexdigest()

    # Generate API key
    api_key = f"PCMD-{plan.upper()[:3]}-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"

    users["users"][user_id] = {
        "id": user_id,
        "username": username,
        "email": email,
        "password_hash": f"{salt}:{pw_hash}",
        "full_name": full_name,
        "whatsapp": whatsapp,
        "role": "user",
        "plan": plan,
        "credits": 0,
        "total_proxies_used": 0,
        "total_searches": 0,
        "total_checks": 0,
        "total_exports": 0,
        "total_favorites": 0,
        "api_key": api_key,
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "login_count": 0,
        "last_ip": None,
        "metadata": {}
    }

    _save_json(USERS_FILE, users)

    # Log creation
    log_activity(user_id, "user_created", {
        "username": username,
        "email": email,
        "plan": plan
    })

    return users["users"][user_id]


def authenticate_user(username_or_email, password):
    """Authenticate user and track login"""
    users = _load_json(USERS_FILE, {"users": {}, "next_id": 1})

    for uid, user in users["users"].items():
        if user["username"] == username_or_email or user["email"] == username_or_email:
            # Verify password
            stored = user["password_hash"]
            salt, pw_hash = stored.split(":")
            if hashlib.sha256((password + salt).encode()).hexdigest() == pw_hash:
                # Update login info
                user["last_login"] = datetime.now().isoformat()
                user["login_count"] += 1
                _save_json(USERS_FILE, users)

                # Log login
                log_activity(uid, "login", {
                    "login_number": user["login_count"],
                    "method": "password"
                })

                # Create session
                session_id = create_session(uid)

                return user, session_id
    return None, None


def get_user_by_id(user_id):
    """Get user by ID"""
    users = _load_json(USERS_FILE, {"users": {}, "next_id": 1})
    return users["users"].get(str(user_id))


def get_user_by_api_key(api_key):
    """Get user by API key"""
    users = _load_json(USERS_FILE, {"users": {}, "next_id": 1})
    for uid, user in users["users"].items():
        if user["api_key"] == api_key and user["is_active"]:
            return user
    return None


def get_all_tracked_users():
    """Get all users"""
    users = _load_json(USERS_FILE, {"users": {}, "next_id": 1})
    return list(users["users"].values())


def update_user_credits(user_id, amount, reason=""):
    """Update user credits"""
    users = _load_json(USERS_FILE, {"users": {}, "next_id": 1})
    user = users["users"].get(str(user_id))
    if not user:
        return False

    user["credits"] += amount
    if user["credits"] < 0:
        return False

    _save_json(USERS_FILE, users)

    log_activity(user_id, "credits_updated", {
        "amount": amount,
        "new_balance": user["credits"],
        "reason": reason
    })

    return True


# ==================== SESSION MANAGEMENT ====================

def create_session(user_id):
    """Create a new user session"""
    sessions = _load_json(SESSIONS_FILE, {"sessions": {}})
    session_id = secrets.token_hex(16)

    sessions["sessions"][session_id] = {
        "user_id": str(user_id),
        "created_at": datetime.now().isoformat(),
        "last_activity": datetime.now().isoformat(),
        "actions": 0,
        "active": True
    }

    _save_json(SESSIONS_FILE, sessions)
    return session_id


def update_session(session_id):
    """Update session activity"""
    sessions = _load_json(SESSIONS_FILE, {"sessions": {}})
    if session_id in sessions["sessions"]:
        sessions["sessions"][session_id]["last_activity"] = datetime.now().isoformat()
        sessions["sessions"][session_id]["actions"] += 1
        _save_json(SESSIONS_FILE, sessions)


def end_session(session_id):
    """End a session"""
    sessions = _load_json(SESSIONS_FILE, {"sessions": {}})
    if session_id in sessions["sessions"]:
        sessions["sessions"][session_id]["active"] = False
        sessions["sessions"][session_id]["ended_at"] = datetime.now().isoformat()
        _save_json(SESSIONS_FILE, sessions)


# ==================== ACTIVITY LOGGING ====================

def log_activity(user_id, action, details=None):
    """Log a user activity"""
    _ensure_dir()
    activity = _load_json(ACTIVITY_FILE, {"activities": []})

    entry = {
        "id": len(activity["activities"]) + 1,
        "user_id": str(user_id),
        "action": action,
        "details": details or {},
        "timestamp": datetime.now().isoformat()
    }

    activity["activities"].append(entry)

    # Keep last 10000 activities
    if len(activity["activities"]) > 10000:
        activity["activities"] = activity["activities"][-10000:]

    _save_json(ACTIVITY_FILE, activity)

    # Update user stats
    _update_user_stats(user_id, action)


def _update_user_stats(user_id, action):
    """Update user statistics based on action"""
    users = _load_json(USERS_FILE, {"users": {}, "next_id": 1})
    user = users["users"].get(str(user_id))
    if not user:
        return

    if action == "proxy_search":
        user["total_searches"] = user.get("total_searches", 0) + 1
    elif action == "proxy_check":
        user["total_checks"] = user.get("total_checks", 0) + 1
    elif action == "proxy_export":
        user["total_exports"] = user.get("total_exports", 0) + 1
    elif action == "favorite_added":
        user["total_favorites"] = user.get("total_favorites", 0) + 1
    elif action == "proxy_used":
        user["total_proxies_used"] = user.get("total_proxies_used", 0) + 1
        user["credits"] = max(0, user.get("credits", 0) - 1)

    _save_json(USERS_FILE, users)


def get_user_activity(user_id, limit=50):
    """Get activity log for a user"""
    activity = _load_json(ACTIVITY_FILE, {"activities": []})
    user_activities = [a for a in activity["activities"] if a["user_id"] == str(user_id)]
    return sorted(user_activities, key=lambda x: x["timestamp"], reverse=True)[:limit]


def get_user_stats(user_id):
    """Get comprehensive user stats"""
    user = get_user_by_id(user_id)
    if not user:
        return None

    activities = get_user_activity(user_id, limit=1000)

    # Calculate stats
    total_time = 0
    if len(activities) >= 2:
        try:
            first = datetime.fromisoformat(activities[-1]["timestamp"])
            last = datetime.fromisoformat(activities[0]["timestamp"])
            total_time = (last - first).total_seconds() / 3600  # hours
        except:
            pass

    return {
        "user": user,
        "total_searches": user.get("total_searches", 0),
        "total_checks": user.get("total_checks", 0),
        "total_exports": user.get("total_exports", 0),
        "total_favorites": user.get("total_favorites", 0),
        "total_proxies_used": user.get("total_proxies_used", 0),
        "credits": user.get("credits", 0),
        "login_count": user.get("login_count", 0),
        "hours_active": round(total_time, 1),
        "recent_activities": activities[:10]
    }


# ==================== PAYMENT TRACKING ====================

def log_payment(user_id, amount, currency, method, tx_hash=None, plan=None):
    """Log a crypto payment"""
    payments = _load_json(PAYMENTS_FILE, {"payments": []})

    payment = {
        "id": len(payments["payments"]) + 1,
        "user_id": str(user_id),
        "amount": amount,
        "currency": currency,
        "method": method,
        "tx_hash": tx_hash,
        "plan": plan,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "confirmed_at": None
    }

    payments["payments"].append(payment)
    _save_json(PAYMENTS_FILE, payments)

    log_activity(user_id, "payment_initiated", {
        "amount": amount,
        "currency": currency,
        "method": method,
        "plan": plan
    })

    return payment


def confirm_payment(payment_id, tx_hash=None):
    """Confirm a payment"""
    payments = _load_json(PAYMENTS_FILE, {"payments": []})
    for p in payments["payments"]:
        if p["id"] == payment_id:
            p["status"] = "confirmed"
            p["confirmed_at"] = datetime.now().isoformat()
            if tx_hash:
                p["tx_hash"] = tx_hash
            _save_json(PAYMENTS_FILE, payments)

            log_activity(p["user_id"], "payment_confirmed", {
                "amount": p["amount"],
                "currency": p["currency"],
                "tx_hash": tx_hash
            })
            return p
    return None


def get_user_payments(user_id):
    """Get all payments for a user"""
    payments = _load_json(PAYMENTS_FILE, {"payments": []})
    return [p for p in payments["payments"] if p["user_id"] == str(user_id)]


def get_all_payments():
    """Get all payments"""
    payments = _load_json(PAYMENTS_FILE, {"payments": []})
    return payments["payments"]


# ==================== GLOBAL STATS ====================

def get_global_stats():
    """Get global platform statistics"""
    users = _load_json(USERS_FILE, {"users": {}, "next_id": 1})
    activity = _load_json(ACTIVITY_FILE, {"activities": []})
    payments = _load_json(PAYMENTS_FILE, {"payments": []})

    all_users = list(users["users"].values())
    active_users = [u for u in all_users if u.get("is_active")]
    paid_users = [u for u in all_users if u.get("credits", 0) > 0]

    total_revenue = sum(p["amount"] for p in payments["payments"] if p["status"] == "confirmed")

    # Activity by day (last 7 days)
    from datetime import timedelta
    now = datetime.now()
    daily_activity = {}
    for i in range(7):
        day = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        daily_activity[day] = len([
            a for a in activity["activities"]
            if a["timestamp"].startswith(day)
        ])

    return {
        "total_users": len(all_users),
        "active_users": len(active_users),
        "paid_users": len(paid_users),
        "total_activities": len(activity["activities"]),
        "total_payments": len(payments["payments"]),
        "total_revenue": total_revenue,
        "daily_activity": daily_activity,
        "credits_in_circulation": sum(u.get("credits", 0) for u in all_users),
        "avg_credits_per_user": round(sum(u.get("credits", 0) for u in all_users) / max(len(all_users), 1), 1)
    }


# ==================== INIT ====================

def init_tracker():
    """Initialize the tracking system"""
    _ensure_dir()
    # Create files if they don't exist
    if not USERS_FILE.exists():
        _save_json(USERS_FILE, {"users": {}, "next_id": 1})
    if not ACTIVITY_FILE.exists():
        _save_json(ACTIVITY_FILE, {"activities": []})
    if not SESSIONS_FILE.exists():
        _save_json(SESSIONS_FILE, {"sessions": {}})
    if not PAYMENTS_FILE.exists():
        _save_json(PAYMENTS_FILE, {"payments": []})
    if not STATS_FILE.exists():
        _save_json(STATS_FILE, {"updated_at": datetime.now().isoformat()})


# Auto-init on import
init_tracker()
