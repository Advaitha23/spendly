import importlib
import sys

import pytest


@pytest.fixture
def app(tmp_path, monkeypatch):
    """A Flask app wired to a throwaway SQLite file, freshly seeded per test."""
    import database.db as db_module

    monkeypatch.setattr(db_module, "DB_PATH", tmp_path / "test_expense_tracker.db")

    sys.modules.pop("app", None)
    app_module = importlib.import_module("app")
    app_module.app.config.update(TESTING=True)

    yield app_module.app

    sys.modules.pop("app", None)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def demo_user_id(app):
    from database.db import get_user_by_email

    return get_user_by_email("demo@spendly.com")["id"]


@pytest.fixture
def logged_in_client(client, demo_user_id):
    with client.session_transaction() as session:
        session["user_id"] = demo_user_id
        session["user_name"] = "Demo User"
    return client
