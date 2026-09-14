# Spec: Registration

## Overview
This step wires up real account creation for Spendly. The `register.html` template and `GET /register` route already exist from earlier scaffolding, but submitting the form does nothing — there is no `POST` handler and no code path that writes a user to the database. This step implements that handler: validating the submitted form, hashing the password, inserting the new user via `database/db.py`, and redirecting to the login page. It is the first feature to exercise the database layer built in Step 1 for real user input.

## Depends on
Step 1 (Database setup) — requires `get_db()` / `init_db()` and the `users` table to already exist and work as implemented in `database/db.py`.

## Routes
- `GET /register` — renders the registration form (unchanged, already implemented) — public
- `POST /register` — validates the form, creates the user, redirects to `/login` on success or re-renders the form with an error on failure — public

## Database changes
No new tables or columns — the `users` table from Step 1 (`id`, `name`, `email`, `password_hash`, `created_at`) already covers registration.

Add two functions to `database/db.py`:
- `get_user_by_email(email)` — returns the matching user row, or `None`
- `create_user(name, email, password_hash)` — inserts a new user and returns the new row's id

## Templates
- **Create:** none
- **Modify:** none — `register.html` already posts to `/register` and already renders an `error` variable inside `.auth-error` when present; the new route just needs to supply that variable on failure

## Files to change
- `database/db.py` — add `get_user_by_email()` and `create_user()`
- `app.py` — change the `/register` route to accept `GET` and `POST`, and implement the `POST` handling logic described above

## Files to create
None

## New dependencies
No new dependencies — `werkzeug.security` (password hashing) is already used in `database/db.py`.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate on the server even though the form has `required`/`type="email"` attributes client-side (name, email, password all required; password minimum 8 characters, matching the form's own placeholder hint)
- Reject duplicate emails using `get_user_by_email()` before inserting, and surface it as the same `error` message the template already supports — do not rely on the `UNIQUE` constraint alone to prevent a raw `sqlite3.IntegrityError` from reaching the user

## Definition of done
- [ ] `GET /register` still renders the existing form unchanged
- [ ] Submitting valid name/email/password creates a new row in `users` with a hashed (not plaintext) password
- [ ] On success, the browser is redirected to `/login`
- [ ] Submitting an email that already exists in `users` re-renders `register.html` with an error message and does not insert a duplicate row
- [ ] Submitting a password under 8 characters re-renders `register.html` with an error message and does not insert a row
- [ ] Submitting with any of name/email/password empty re-renders `register.html` with an error message and does not insert a row
- [ ] Restarting the app afterward does not duplicate the seeded demo user or any newly registered users (`seed_db()` still only seeds once)
