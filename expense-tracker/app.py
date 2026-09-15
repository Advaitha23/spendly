from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from database.db import get_db, init_db, seed_db, get_user_by_email, create_user

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            return render_template("register.html", error="All fields are required.")

        if len(password) < 8:
            return render_template("register.html", error="Password must be at least 8 characters.")

        if get_user_by_email(email) is not None:
            return render_template("register.html", error="An account with that email already exists.")

        password_hash = generate_password_hash(password)
        create_user(name, email, password_hash)
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_email(email)
        if user is None or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid email or password.")

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user = {
        "name": "Demo User",
        "email": "demo@spendly.com",
        "initials": "DU",
        "member_since": "January 2025",
    }

    stats = [
        {"label": "Total spent", "value": "₹266.24"},
        {"label": "Transactions", "value": "5"},
        {"label": "Top category", "value": "Bills"},
    ]

    transactions = [
        {"date": "12 Sep 2026", "description": "Groceries", "category": "Food", "category_slug": "food", "amount": 42.50},
        {"date": "10 Sep 2026", "description": "Bus pass", "category": "Transport", "category_slug": "transport", "amount": 15.00},
        {"date": "08 Sep 2026", "description": "Electricity bill", "category": "Bills", "category_slug": "bills", "amount": 89.99},
        {"date": "05 Sep 2026", "description": "Pharmacy", "category": "Health", "category_slug": "health", "amount": 60.00},
        {"date": "03 Sep 2026", "description": "Movie tickets", "category": "Entertainment", "category_slug": "entertainment", "amount": 25.00},
    ]

    categories = [
        {"name": "Bills", "slug": "bills", "total": 89.99, "percent": 34},
        {"name": "Food", "slug": "food", "total": 76.25, "percent": 29},
        {"name": "Health", "slug": "health", "total": 60.00, "percent": 22},
        {"name": "Entertainment", "slug": "entertainment", "total": 25.00, "percent": 9},
        {"name": "Transport", "slug": "transport", "total": 15.00, "percent": 6},
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
    )


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
