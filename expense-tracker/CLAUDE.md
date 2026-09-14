# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Spendly is a personal expense-tracking web app built as a Flask learning scaffold. Routes and modules are added incrementally in numbered "Steps" (see comments in `app.py` and `database/db.py`); several routes and the database layer are intentionally unimplemented placeholders (`logout`, `profile`, `add_expense`, `edit_expense`, `delete_expense` return plain placeholder strings, and `database/db.py` has no code yet — only a comment describing the `get_db()` / `init_db()` / `seed_db()` functions students are expected to write).

## Commands

Run from `expense-tracker/expense-tracker/` (the actual app root — note the repo has a nested `expense-tracker/expense-tracker/` layout).

```bash
# activate the venv (already created at expense-tracker/venv)
source ../venv/bin/activate

# run the dev server — listens on port 5001, not Flask's default 5000
python3 app.py

# run tests (pytest-flask is a declared dependency, but no test files exist yet)
pytest
```

There is no build step, linter, or frontend bundler — templates and static assets are served directly by Flask.

## Architecture

- **`app.py`** — single Flask app, all routes defined directly here (no blueprints). Each route calls `render_template()` with no view logic yet beyond that.
- **`database/db.py`** — intended home for all SQLite access (`get_db()`, `init_db()`, `seed_db()`); currently unimplemented.
- **`templates/base.html`** — the shared layout every page extends via `{% extends "base.html" %}`. It owns the `<head>` (Google Fonts: DM Serif Display + DM Sans at weights 300/400/500/600 only — nothing heavier is loaded), the navbar, and the footer (including the Terms/Privacy links). Page templates should not duplicate this chrome.
  - Extension points child templates use to add page-scoped CSS/JS without editing `base.html`: `{% block head %}` (extra `<style>`/`<link>` tags) and `{% block scripts %}` (extra `<script>` tags), plus `{% block title %}` and `{% block content %}`.
- **`static/css/style.css`** — the one and only stylesheet for the whole site (there is no `landing.css` or per-page CSS file). It's organized as sequential labeled sections (Variables, Reset, Navbar, Hero, Legal pages, Footer, etc.) and driven by CSS custom properties defined once in `:root` (colors like `--ink`/`--accent`, fonts, radii, `--max-width`). New styles should reuse these tokens rather than hardcoding new colors/fonts, and should be added as a new labeled section rather than mixed into unrelated ones.
- **`static/js/main.js`** — currently empty/placeholder; intended to hold vanilla JS as features are built (no JS framework is used anywhere in this project — see the video modal in `landing.html` for the established pattern of page-scoped vanilla JS via `{% block scripts %}`).
- **`templates/legal-*` pattern** — `terms.html` and `privacy.html` both use shared `.legal-section` / `.legal-container` / `.legal-header` / `.legal-card` classes from `style.css`; follow this structure for any future legal/static content page rather than inventing new markup.
