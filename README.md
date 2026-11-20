# PixelVault Games — Website Spoofing Educational Demonstration

**CECS Semester Project — Group 8 — "Website Spoofing with Mock Login"**

> ⚠️ **Educational use only.** Everything here runs on `localhost`. The "spoofed"
> site is a self-revealing teaching tool: it accepts only synthetic demo input,
> **never stores or logs submitted passwords**, and shows an educational reveal
> after any submission. It does not impersonate any real company. "GTA VI" appears
> only as a text product title; all artwork is original placeholder art.

## What this project contains

Three tiny Flask apps that run side by side on different ports (different *origins*),
so you can see, in a browser, the difference between a real store and a convincing fake.

| App | Folder | Port | Origin | Role |
|-----|--------|------|--------|------|
| Website A — Legitimate store | `legit_site/` | 5000 | `http://127.0.0.1:5000` | Real auth: register, hashed passwords, sessions, protected account page |
| Website B — Spoof simulation | `spoof_site/` | 5001 | `http://127.0.0.1:5001` | Look-alike front-end, **non-harvesting** mock login, educational reveal |
| Comparison dashboard | `dashboard/` | 5002 | `http://127.0.0.1:5002` | Side-by-side event log of both origins |

The whole point of using three ports is that **the browser treats them as three
different websites**, exactly the way `yourbank.com` and `your-bank-login.com` are
different sites. That origin difference is the real lesson.

## Install (Windows)

1. Install Python 3.10+ from python.org (check "Add Python to PATH" during install).
2. Open **Command Prompt** in the project folder and create a virtual environment:

   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Initialize the databases

```
python legit_site\database.py
```

This creates `legit_site\pixelvault.db` with two demo accounts (see below).
The spoof site and dashboard create their own event-log DBs automatically on first run.

## Run (three terminals, all with the venv activated)

```
Terminal 1:   python legit_site\app.py
Terminal 2:   python spoof_site\app.py
Terminal 3:   python dashboard\app.py
```

Then open:
- Legit store: http://127.0.0.1:5000
- Spoof demo:  http://127.0.0.1:5001
- Dashboard:   http://127.0.0.1:5002

## Demo accounts (fictional, for the legit site)

| Email | Password |
|-------|----------|
| `demo@pixelvault.test` | `Demo-Pass-123` |
| `student@pixelvault.test` | `Beach-2026!` |

The spoof site has its own designated synthetic value shown on its page; it does not
share a database with the legit site and cannot authenticate anyone.

## Folder map

```
pixelvault-project/
├── README.md
├── requirements.txt
├── legit_site/          # Website A
│   ├── app.py
│   ├── database.py      # creates DB + seeds demo users
│   ├── schema.sql
│   ├── templates/
│   └── static/
├── spoof_site/          # Website B
│   ├── app.py
│   ├── events.py        # non-sensitive event logging (NO passwords)
│   ├── templates/
│   └── static/
├── dashboard/           # comparison view
│   ├── app.py
│   └── templates/
└── docs/
    ├── architecture.md
    ├── walkthrough.md
    ├── devtools_guide.md
    ├── security_comparison.md
    └── professor_questions.md
```

See `docs/` for the architecture diagram, demo scripts, the Chrome DevTools guide,
and anticipated professor questions with answers.
