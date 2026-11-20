"""
Comparison dashboard.

Reads the two independent event sources and shows them side by side:
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


def read_legit_events():
    if not os.path.exists(LEGIT_DB):
        return []
    conn = sqlite3.connect(LEGIT_DB)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT ts, origin, method, email_tried, outcome "
            "FROM login_events ORDER BY id DESC LIMIT 100"
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    return [dict(r) for r in rows]


def read_spoof_events():
    if not os.path.exists(SPOOF_DB):
        return []
    conn = sqlite3.connect(SPOOF_DB)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT ts, origin, method, outcome "
            "FROM mock_events ORDER BY id DESC LIMIT 100"
        ).fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    return [dict(r) for r in rows]


@app.route("/")
def index():
    legit = read_legit_events()
    spoof = read_spoof_events()
    comparison = [
        ("Origin", LEGIT_ORIGIN, SPOOF_ORIGIN),
        ("Has a real user database", "Yes (hashed passwords)", "No"),
        ("Validates credentials", "Yes", "No — accepts nothing for real"),
        ("Stores submitted passwords", "No (only one-way hashes at registration)",
         "No (discarded immediately)"),
        ("Issues an authenticated session", "Yes, on success", "Never"),
        ("Password manager autofills here", "Yes (its own origin)",
         "No (different origin)"),
        ("Shows urgency / discount pressure", "No", "Yes (by design, to teach)"),
    ]
    return render_template(
        "dashboard.html",
        legit=legit, spoof=spoof, comparison=comparison,
        legit_origin=LEGIT_ORIGIN, spoof_origin=SPOOF_ORIGIN,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)
