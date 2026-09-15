import sqlite3
from datetime import date, timedelta
from pathlib import Path
from werkzeug.security import generate_password_hash

DB_PATH = Path(__file__).resolve().parent.parent / "expense_tracker.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # per-connection setting; must be set every time
    return conn


def get_user_by_email(email):
    conn = get_db()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    conn.close()
    return row


def create_user(name, email, password_hash):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, password_hash),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    cur = conn.cursor()

    if cur.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        conn.close()
        return

    cur.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
    )
    user_id = cur.lastrowid

    today = date.today()

    def offset(days_back):
        target = today - timedelta(days=days_back)
        if target.month != today.month:  # never spill into the previous month
            target = today.replace(day=1)
        return target.isoformat()

    expenses = [
        (user_id, 42.50, "Food", offset(1), "Groceries"),
        (user_id, 15.00, "Transport", offset(2), "Bus pass"),
        (user_id, 89.99, "Bills", offset(3), "Electricity bill"),
        (user_id, 60.00, "Health", offset(5), "Pharmacy"),
        (user_id, 25.00, "Entertainment", offset(7), "Movie tickets"),
        (user_id, 120.00, "Shopping", offset(9), "New shoes"),
        (user_id, 10.00, "Other", offset(11), "Miscellaneous"),
        (user_id, 33.75, "Food", offset(13), "Lunch out"),
    ]
    cur.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        expenses,
    )
    conn.commit()
    conn.close()
