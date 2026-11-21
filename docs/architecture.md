# Architecture

## The big picture

Three small Flask applications run at the same time on one computer, each on its
own port. Because browsers treat `scheme + host + port` as the **origin**, these
are three separate websites as far as the browser (and any password manager) is
concerned.

```
                         ┌─────────────────────────────┐
                         │          Browser            │
                         │   (Chrome, DevTools open)   │
                         └──────┬───────────┬──────────┘
                                │           │
              HTTP GET/POST     │           │   HTTP GET/POST
                                ▼           ▼
        ┌───────────────────────────┐   ┌───────────────────────────┐
        │  Website A — LEGIT         │   │  Website B — SPOOF         │
        │  Flask @ 127.0.0.1:5000    │   │  Flask @ 127.0.0.1:5001    │
        │                            │   │                            │
        │  • register / login/logout │   │  • look-alike pages        │
        │  • check_password_hash     │   │  • urgency + discount       │
        │  • Flask session cookie    │   │  • mock login (no auth)     │
        │  • protected /account      │   │  • discards password        │
        └──────────────┬─────────────┘   └──────────────┬─────────────┘
                       │                                 │
                       ▼                                 ▼
             ┌───────────────────┐             ┌───────────────────┐
             │  pixelvault.db    │             │  spoof_events.db  │
             │  (SQLite)         │             │  (SQLite)         │
             │  users (hashes)   │             │  mock_events      │
             │  login_events     │             │  (NO password col)│
             └─────────┬─────────┘             └─────────┬─────────┘
                       │                                 │
                       └──────────────┬──────────────────┘
                                      ▼
                        ┌───────────────────────────┐
                        │  Comparison Dashboard      │
                        │  Flask @ 127.0.0.1:5002    │
                        │  reads both DBs, read-only │
                        └───────────────────────────┘
```

## Request lifecycle (legit login)

1. Browser sends `GET /login` to `127.0.0.1:5000`. Flask renders `login.html`.
2. User submits the form: `POST /login` with `email`, `password`, and a `_csrf` token.
3. Flask checks the CSRF token against the session. If bad → HTTP 400.
4. Flask looks up the user row in SQLite and calls
   `check_password_hash(stored_hash, submitted_password)`.
5. On success, Flask stores `user_email` in the signed session cookie and redirects
   to `/account`. On failure, it re-renders the form with an error.
6. `GET /account` reads the session cookie; no valid session → redirect to `/login`.

## Request lifecycle (spoof mock login)

1. Browser sends `GET /login` to `127.0.0.1:5001` (a **different origin**).
2. User submits: `POST /login`.
3. The handler reads the fields into local variables and **immediately discards the
   password** (`del`). Nothing is written anywhere with it.
4. It records a non-sensitive event — `ts, origin, method, outcome` — and re-renders
   the form with an "Invalid email or password." error. A separate `/about` page
   explains the spoof-vs-real difference in plain terms.

## Why three ports instead of one app

Using distinct origins is the whole lesson. It lets you demonstrate, live:
- the address bar differs,
- the password manager autofills on 5000 but not 5001,
- a passkey (if added) would bind to 5000 and fail on 5001.

## Files at a glance

| File | Purpose |
|------|---------|
| `legit_site/app.py` | Routes + real auth logic for Website A |
| `legit_site/database.py` | Creates the DB, seeds demo users (hashed) |
| `legit_site/schema.sql` | `users` and `login_events` tables |
| `spoof_site/app.py` | Routes for Website B; discards submitted password |
| `spoof_site/events.py` | Event logger with **no password field** |
| `dashboard/app.py` | Read-only view of both event sources |
| `*/templates/*.html` | Jinja2 templates |
| `*/static/css/style.css` | Styling (dark theme) |
| `*/static/js/main.js` | Legit: none meaningful. Spoof: countdown + popup only |
