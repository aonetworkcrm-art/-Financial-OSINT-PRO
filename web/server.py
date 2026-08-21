"""
🎯 NEXUS INTEL — Web Server
Landing page + Registro + Pagos + Admin
"""
import os
import sys
import secrets
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash

sys.path.insert(0, str(Path(__file__).parent.parent))
from database import (
    init_db, create_user, login_user, get_db,
    create_order, approve_order, get_all_orders, get_pending_orders,
    get_user, get_all_users, get_user_stats, get_dashboard_stats
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 86400

# Init DB on import (gunicorn won't run __main__)
with app.app_context():
    init_db()

CONFIG = {
    "paypal_email": "tu-paypal@email.com",
    "whatsapp": "+573001234567",
    "wallet_address": "0xYOUR_WALLET",
    "email": "admin@nexusintel.com",
    "tool_url": "http://localhost:8502",
}

PLANS = {
    "starter": {
        "name": "Starter", "price": 29, "searches": 50,
        "features": ["50 búsquedas/mes", "Búsqueda por dirección", "Email, phone, banco", "Credit score", "CSV export"],
    },
    "professional": {
        "name": "Professional", "price": 79, "searches": 200,
        "features": ["200 búsquedas/mes", "SSN → Identidad", "Reverse lookup", "Lotes 50+", "Passwords", "API Access"],
    },
    "enterprise": {
        "name": "Enterprise", "price": 199, "searches": 1000,
        "features": ["1,000 búsquedas/mes", "Lotes 500+", "Dark web data", "Integración custom", "Soporte 24/7"],
    },
}


@app.route("/")
def index():
    return render_template("index.html", plans=PLANS, config=CONFIG)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()
        whatsapp = request.form.get("whatsapp", "").strip()
        plan = request.form.get("plan", "professional")

        if not username or not email or not password:
            flash("Completa todos los campos", "danger")
            return render_template("register.html", config=CONFIG, selected_plan=plan)

        user = create_user(username, email, password, full_name, whatsapp)
        if not user:
            flash("El usuario o email ya existe", "danger")
            return render_template("register.html", config=CONFIG, selected_plan=plan)

        session.permanent = True
        session["user_id"] = user["id"]
        flash(f"¡Bienvenido {username}!", "success")
        return redirect(url_for("checkout", plan_id=plan))

    selected = request.args.get("plan", "professional")
    return render_template("register.html", config=CONFIG, selected_plan=selected)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = login_user(username, password)
        if user:
            session.permanent = True
            session["user_id"] = user["id"]
            if user["role"] == "admin":
                return redirect(url_for("admin"))
            return redirect(url_for("panel"))
        flash("Credenciales incorrectas", "danger")
    return render_template("login.html", config=CONFIG)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/checkout/<plan_id>", methods=["GET", "POST"])
def checkout(plan_id):
    if plan_id not in PLANS:
        return redirect(url_for("index"))
    plan = PLANS[plan_id]

    if request.method == "POST":
        payment_method = request.form.get("payment_method", "paypal")
        order_id = f"NEX-{secrets.token_hex(8).upper()}"

        create_order(
            order_id=order_id,
            user_id=session.get("user_id"),
            plan=plan_id,
            price=plan["price"],
            searches=plan["searches"],
            payment_method=payment_method,
        )

        if payment_method == "paypal":
            return redirect(url_for("payment_paypal", order_id=order_id))
        elif payment_method == "crypto":
            return redirect(url_for("payment_crypto", order_id=order_id))
        elif payment_method == "whatsapp":
            return redirect(url_for("payment_whatsapp", order_id=order_id))

    return render_template("checkout.html", plan=plan, plan_id=plan_id, config=CONFIG)


@app.route("/payment/paypal/<order_id>")
def payment_paypal(order_id):
    conn = get_db()
    order = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    conn.close()
    if not order:
        return redirect(url_for("index"))
    order = dict(order)
    paypal_link = f"https://www.paypal.com/paypalme/{CONFIG['paypal_email'].split('@')[0]}?amount={order['price']}&currencyCode=USD&memo=NexusIntel-{order_id[:8]}"
    return render_template("payment_paypal.html", order=order, order_id=order_id, paypal_link=paypal_link, config=CONFIG)


@app.route("/payment/crypto/<order_id>")
def payment_crypto(order_id):
    conn = get_db()
    order = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    conn.close()
    if not order:
        return redirect(url_for("index"))
    return render_template("payment_crypto.html", order=dict(order), order_id=order_id, config=CONFIG)


@app.route("/payment/whatsapp/<order_id>")
def payment_whatsapp(order_id):
    conn = get_db()
    order = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    conn.close()
    if not order:
        return redirect(url_for("index"))
    order = dict(order)
    wa_number = CONFIG["whatsapp"].replace("+", "").replace(" ", "")
    msg = f"Hola, quiero activar NEXUS INTEL. Orden: {order_id}. Plan: {order['plan']} ${order['price']}"
    wa_link = f"https://wa.me/{wa_number}?text={msg}"
    return render_template("payment_whatsapp.html", order=order, order_id=order_id, wa_link=wa_link, config=CONFIG)


@app.route("/confirm/<order_id>", methods=["POST"])
def confirm_payment(order_id):
    conn = get_db()
    conn.execute("UPDATE orders SET status = 'reported' WHERE order_id = ?", (order_id,))
    conn.commit()
    conn.close()
    flash("Pago reportado. Será verificado pronto.", "success")
    return redirect(url_for("panel"))


@app.route("/panel")
def panel():
    if "user_id" not in session:
        return redirect(url_for("login"))
    stats = get_user_stats(session["user_id"])
    return render_template("panel.html", config=CONFIG, stats=stats)


@app.route("/admin")
def admin():
    if "user_id" not in session:
        return redirect(url_for("login"))
    dashboard = get_dashboard_stats()
    all_orders = get_all_orders()
    pending = get_pending_orders()
    users = get_all_users()
    return render_template("admin.html", stats=dashboard, all_orders=all_orders, pending_orders=pending, all_users=users)


@app.route("/admin/approve/<order_id>", methods=["POST"])
def admin_approve(order_id):
    result = approve_order(order_id)
    if result:
        return jsonify({"success": True, "token": result["api_token"]})
    return jsonify({"error": "Not found"}), 404


@app.route("/api/orders")
def api_orders():
    orders = get_all_orders()
    return jsonify(orders)


if __name__ == "__main__":
    init_db()
    print("=" * 60)
    print("⚡ NEXUS INTEL — Web Server")
    print("=" * 60)
    print("Landing: http://localhost:5000")
    print("Admin:   http://localhost:5000/admin")
    print("=" * 60)
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=False)
