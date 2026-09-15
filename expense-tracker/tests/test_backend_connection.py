import pytest

from database.db import create_user
from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
)

# The seeded demo user has 8 expenses totalling 396.24, with "Shopping" (120.00)
# as the single highest category — not 346.24 / "Bills" from the spec, which
# was carried over from the Step 4 hardcoded placeholder data.
SEED_TOTAL = 396.24
SEED_COUNT = 8
SEED_TOP_CATEGORY = "Shopping"


@pytest.fixture
def user_with_no_expenses(app):
    from werkzeug.security import generate_password_hash

    return create_user("No Expenses", "noexpenses@example.com", generate_password_hash("password123"))


# ------------------------------------------------------------------ #
# get_user_by_id                                                      #
# ------------------------------------------------------------------ #

def test_get_user_by_id_returns_correct_user(app, demo_user_id):
    user = get_user_by_id(demo_user_id)

    assert user["name"] == "Demo User"
    assert user["email"] == "demo@spendly.com"
    assert user["member_since"].split()[1].isdigit()  # "Month YYYY"
    assert len(user["member_since"].split()[1]) == 4


def test_get_user_by_id_returns_none_for_missing_id(app):
    assert get_user_by_id(999999) is None


# ------------------------------------------------------------------ #
# get_summary_stats                                                   #
# ------------------------------------------------------------------ #

def test_get_summary_stats_with_expenses(app, demo_user_id):
    stats = get_summary_stats(demo_user_id)

    assert stats["total_spent"] == pytest.approx(SEED_TOTAL)
    assert stats["transaction_count"] == SEED_COUNT
    assert stats["top_category"] == SEED_TOP_CATEGORY


def test_get_summary_stats_with_no_expenses(app, user_with_no_expenses):
    stats = get_summary_stats(user_with_no_expenses)

    assert stats == {"total_spent": 0, "transaction_count": 0, "top_category": "—"}


# ------------------------------------------------------------------ #
# get_recent_transactions                                             #
# ------------------------------------------------------------------ #

def test_get_recent_transactions_ordered_newest_first(app, demo_user_id):
    transactions = get_recent_transactions(demo_user_id)

    assert len(transactions) == SEED_COUNT
    assert transactions[0]["description"] == "Groceries"  # most recent (1 day back)
    assert transactions[-1]["description"] == "Lunch out"  # oldest (13 days back)
    for tx in transactions:
        assert set(tx.keys()) == {"date", "description", "category", "amount"}


def test_get_recent_transactions_with_no_expenses(app, user_with_no_expenses):
    assert get_recent_transactions(user_with_no_expenses) == []


# ------------------------------------------------------------------ #
# get_category_breakdown                                              #
# ------------------------------------------------------------------ #

def test_get_category_breakdown_with_expenses(app, demo_user_id):
    breakdown = get_category_breakdown(demo_user_id)

    assert [row["name"] for row in breakdown] == sorted(
        [row["name"] for row in breakdown],
        key=lambda name: next(r["amount"] for r in breakdown if r["name"] == name),
        reverse=True,
    )
    assert breakdown[0]["name"] == SEED_TOP_CATEGORY
    assert all(isinstance(row["pct"], int) for row in breakdown)
    assert sum(row["pct"] for row in breakdown) == 100


def test_get_category_breakdown_with_no_expenses(app, user_with_no_expenses):
    assert get_category_breakdown(user_with_no_expenses) == []


# ------------------------------------------------------------------ #
# GET /profile                                                        #
# ------------------------------------------------------------------ #

def test_profile_redirects_when_not_logged_in(client):
    response = client.get("/profile")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_profile_shows_real_data_for_seed_user(logged_in_client):
    response = logged_in_client.get("/profile")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Demo User" in body
    assert "demo@spendly.com" in body
    assert "₹" in body
    assert "₹396.24" in body
    assert "Shopping" in body
    # newest-first ordering
    assert body.index("Groceries") < body.index("Lunch out")
    # all 7 seeded categories appear in the breakdown
    for category in ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]:
        assert category in body


def test_profile_handles_user_with_no_expenses(client, user_with_no_expenses):
    with client.session_transaction() as session:
        session["user_id"] = user_with_no_expenses
        session["user_name"] = "No Expenses"

    response = client.get("/profile")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "₹0.00" in body
