"""
Comparison dashboard.

Reads the two independent event sources and presents them as one clear story:
  - legit_site/pixelvault.db   -> login_events   (real authentication outcomes)
  - spoof_site/spoof_events.db -> mock_events    (non-sensitive simulation events)

It never shows passwords, session tokens, or visitor identities, because those
were never recorded in the first place.

Run:  python dashboard/app.py   ->  http://127.0.0.1:5002
"""
import os
import sqlite3

from flask import Flask, render_template

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LEGIT_DB = os.path.join(ROOT, "legit_site", "pixelvault.db")
SPOOF_DB = os.path.join(ROOT, "spoof_site", "spoof_events.db")

LEGIT_ORIGIN = "http://127.0.0.1:5000"
SPOOF_ORIGIN = "http://127.0.0.1:5001"

app = Flask(__name__)


def _read(db_path, query):
    if not os.path.exists(db_path):
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(query).fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    return [dict(r) for r in rows]


def read_legit_events():
    return _read(LEGIT_DB,
                 "SELECT ts, origin, method, email_tried, outcome "
                 "FROM login_events ORDER BY id DESC LIMIT 100")


def read_spoof_events():
    return _read(SPOOF_DB,
                 "SELECT ts, origin, method, outcome "
                 "FROM mock_events ORDER BY id DESC LIMIT 100")


@app.route("/")
def index():
    legit = read_legit_events()
    spoof = read_spoof_events()

    # Headline numbers for the presenter to point at.
    legit_success = sum(1 for e in legit if e["outcome"] == "success")
    legit_failed = sum(1 for e in legit if e["outcome"] == "invalid_credentials")
    spoof_submits = sum(1 for e in spoof
                        if e["outcome"] in ("mock_login_submitted", "mock_signup_submitted"))

    stats = [
        {"label": "Real logins succeeded", "value": legit_success, "tone": "good",
         "note": "Validated against hashed passwords on the real site."},
        {"label": "Credentials submitted to the spoof", "value": spoof_submits,
         "tone": "warn", "note": "Each one would be a victim on a real phishing page."},
        {"label": "Passwords the spoof stored", "value": 0, "tone": "key",
         "note": "The spoof has no field for a password. This stays 0 by design."},
        {"label": "Distinct origins", "value": 2, "tone": "neutral",
         "note": "Two different websites — the lesson hides in the address bar."},
    ]

    comparison = [
        ("What the user types goes to", LEGIT_ORIGIN, SPOOF_ORIGIN),
        ("Real account database", "Yes — emails + hashed passwords", "None"),
        ("Validates the password", "Yes (check_password_hash)", "No — rejects everyone"),
        ("Stores the submitted password", "Never (one-way hash at signup only)",
         "Never (read, then discarded)"),
        ("Grants a logged-in session", "Yes, on success", "Never"),
        ("Password manager autofills", "Yes — same origin", "No — different origin"),
        ("Uses urgency / discounts", "No", "Yes — to show the pressure tactic"),
    ]

    return render_template(
        "dashboard.html",
        legit=legit, spoof=spoof, stats=stats, comparison=comparison,
        legit_origin=LEGIT_ORIGIN, spoof_origin=SPOOF_ORIGIN,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=False)
