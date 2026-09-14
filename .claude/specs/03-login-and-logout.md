# Spec: Login and Logout

## Overview
This step makes the existing (but non-functional) `login.html` form and the placeholder `/logout` route actually work: authenticating a submitted email/password against the `users` table created in Step 1 and populated by Step 2's registration, starting a Flask session on success, and letting the user end that session via logout. It also updates the shared navbar so it reflects whether a session is active — until now the nav has always shown static "Sign in" / "Get started" links regardless of login state. This is the first step to introduce server-side session state; no other route gains authentication enforcement yet (that is left to the routes that need it, in their own future steps).

## Depends on
- Step 1 (Database setup) — the `users` table and `get_db()`.
- Step 2 (Registration) — `get_user_by_email()` in `database/db.py`, and real user rows to authenticate against.

## Routes
- `POST /login` — validate submitted email/password against a registered user, start a session on success and redirect to `/profile`, or re-render `login.html` with a generic error on failure — public
- `GET /login` — renders the login form (unchanged, already implemented) — public
- `GET /logout` — clears the session and redirects to `/login` — logged-in (harmless no-op if no session exists; not otherwise gated, consistent with the rest of the app having no auth enforcement yet)

## Database changes
No new tables or columns, and no new functions — reuses `get_user_by_email()` (added in Step 2) to look up the submitted email; the password is checked with `werkzeug.security.check_password_hash` against the stored `password_hash`.

## Templates
- **Create:** none
- **Modify:** `templates/base.html` — the navbar's `nav-links` block currently always renders "Sign in" + "Get started". Change it to check the session: when a user is logged in, render a single "Logout" link (`{{ url_for('logout') }}`) instead; when not logged in, keep the existing two links unchanged.

`login.html` itself needs no changes — it already POSTs to `/login` and already renders an `error` variable inside `.auth-error` when present, the same pattern `register.html` uses.

## Files to change
- `app.py`:
  - Set `app.secret_key` (a plain hardcoded dev value is fine — this scaffold has no other secret/config management, and session signing is the only thing that needs it)
  - Import `session` from `flask` and `check_password_hash` from `werkzeug.security`
  - Change the `/login` route to accept `GET` and `POST`; implement the `POST` handling described above
  - Replace the placeholder `/logout` route body with real logic: `session.clear()` then `redirect(url_for("login"))`
- `templates/base.html` — conditional nav block described above

## Files to create
None

## New dependencies
No new dependencies — `session` is core Flask, `check_password_hash` is already available via the `werkzeug` dependency already declared.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug (already true for storage; verify with `check_password_hash`, never compare hashes or plaintext directly)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use one generic error message ("Invalid email or password.") for both "no such email" and "wrong password" cases — do not reveal which one was wrong (prevents user enumeration)
- Store only `user_id` in the session — never the password or password hash
- Do not add login-required protection to any other route (`/profile`, `/expenses/...`, etc.) — that belongs to those routes' own future steps, not this one

## Definition of done
- [ ] `GET /login` still renders the existing form unchanged
- [ ] Submitting the demo user's (or any registered) correct email/password logs them in and redirects to `/profile`
- [ ] Submitting an email that isn't registered re-renders `login.html` with the generic invalid-credentials error, and no session is created
- [ ] Submitting a registered email with the wrong password re-renders `login.html` with the same generic error, and no session is created
- [ ] While logged in, the navbar shows "Logout" instead of "Sign in" / "Get started"
- [ ] Visiting `/logout` clears the session and redirects to `/login`
- [ ] After logout, the navbar reverts to showing "Sign in" / "Get started"
- [ ] Restarting the app does not affect the ability to log in with previously registered or seeded credentials (session state is server-side per-process, but user data persists in SQLite)
