# Step 1 — Database Setup: Implementation Plan

## Context

Spendly (the Flask learning-scaffold app in `expense-tracker/expense-tracker/`) is built in numbered Steps. `database/db.py` is currently just a comment stub — no code — and `app.py` has no database wiring at all. Every later step (auth, profile, expense CRUD) depends on a working data layer, so this step implements the SQLite foundation exactly per `.claude/specs/01-database-setup.md`: two tables (`users`, `expenses`), three functions (`get_db`, `init_db`, `seed_db`), and startup wiring in `app.py`. No new routes, no new files, no new dependencies — this is a pure data-layer build-out.

## Approach

### `database/db.py`

```python
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
        if target.month != today.month:      # never spill into the previous month
            target = today.replace(day=1)
        return target.isoformat()

    expenses = [
        (user_id, 42.50, "Food",          offset(1),  "Groceries"),
        (user_id, 15.00, "Transport",     offset(2),  "Bus pass"),
        (user_id, 89.99, "Bills",         offset(3),  "Electricity bill"),
        (user_id, 60.00, "Health",        offset(5),  "Pharmacy"),
        (user_id, 25.00, "Entertainment", offset(7),  "Movie tickets"),
        (user_id, 120.00, "Shopping",     offset(9),  "New shoes"),
        (user_id, 10.00, "Other",         offset(11), "Miscellaneous"),
        (user_id, 33.75, "Food",          offset(13), "Lunch out"),
    ]
    cur.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        expenses,
    )
    conn.commit()
    conn.close()
```

Key decisions:
- **Path resolution** anchors to `Path(__file__)`, not `os.getcwd()`, so `expense_tracker.db` always lands at the app root (`expense-tracker/expense-tracker/`, sibling of `app.py`) regardless of where the process is launched from — matches `.gitignore`'s `expense_tracker.db` entry.
- **`init_db()` uses `executescript()`** with both `CREATE TABLE IF NOT EXISTS` statements in one readable block (mirrors the spec's schema tables) rather than two separate `execute()` calls — no injection concern since it's static DDL with zero interpolation.
- **`DEFAULT (datetime('now'))`** — parens around the function call are required SQLite DDL syntax; easy to typo.
- **Seed dates** are computed relative to `date.today()` (never hardcoded) and clamped to stay within the current month even if `seed_db()` first runs early in the month — satisfies "dates spread across current month" generically.
- **All 7 fixed categories** appear at least once (Food appears twice to reach 8 rows).
- **Every value uses `?` placeholders** — no f-strings/`.format()`/`%` anywhere in SQL.
- **Re-seed guard** checks only `users` count (per spec wording exactly) — each `get_db()` caller opens and closes its own connection; no `g`-based caching, since the spec defines no teardown hook and this is a simplicity-first teaching scaffold.

### `app.py`

Add right after `app = Flask(__name__)`, before the route definitions:

```python
from flask import Flask, render_template

from database.db import get_db, init_db, seed_db

app = Flask(__name__)

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #
...
```

`get_db` is imported now (per spec §6) even though unused in `app.py` itself yet — later steps' routes will call it. Module-level placement (not inside `if __name__ == "__main__":`) means DB setup runs on import too, so it works identically under `python3 app.py` and under `pytest-flask`'s `app` fixture. No other lines in `app.py` change.

## Files to change

- `expense-tracker/expense-tracker/database/db.py` — full implementation (replaces stub comment)
- `expense-tracker/expense-tracker/app.py` — add import + startup block only

No files created, no dependency changes (spec confirms `sqlite3` + `werkzeug.security` are already available).

## Risks / edge cases

- `PRAGMA foreign_keys = ON` is per-connection, not persistent in the db file — every `get_db()` call re-issues it correctly.
- `executescript()` auto-commits any pending transaction first; harmless here since `init_db()` runs standalone.
- Re-seed guard only checks `users`, not `expenses` — matches spec literally; if someone manually wipes just `expenses`, `seed_db()` won't refill it (acceptable per spec).
- No `try/finally` around `conn.close()` — acceptable simplification for this teaching scaffold; not required by the spec.

## Verification (manual, run from the app root with venv active)

1. `rm -f expense_tracker.db` (clean slate), then `python3 app.py` briefly → `ls expense_tracker.db` exists.
2. `sqlite3 expense_tracker.db ".schema users"` / `".schema expenses"` — confirm columns, `UNIQUE`, `NOT NULL`, FK clause match spec.
3. `sqlite3 expense_tracker.db "SELECT name, email, password_hash FROM users;"` — one row, hashed (not plaintext) password.
4. `sqlite3 expense_tracker.db "SELECT category, date, amount FROM expenses ORDER BY date;"` — 8 rows, all 7 categories present, dates in current month, `YYYY-MM-DD`.
5. Restart `python3 app.py` again → re-check counts stay at 1 user / 8 expenses (no duplicate seeding).
6. `sqlite3 expense_tracker.db "INSERT INTO users (name, email, password_hash) VALUES ('X','demo@spendly.com','y');"` → expect `UNIQUE constraint failed`.
7. `sqlite3 expense_tracker.db "PRAGMA foreign_keys=ON; INSERT INTO expenses (user_id, amount, category, date) VALUES (9999, 5.0, 'Food', '2026-09-14');"` → expect `FOREIGN KEY constraint failed`.
8. `python3 app.py` then `curl -o /dev/null -w '%{http_code}\n' http://127.0.0.1:5001/` → `200`, no traceback in server log.
9. `grep -nE '%s|\.format\(|f"' database/db.py` → no matches, confirming parameterized-queries-only.
