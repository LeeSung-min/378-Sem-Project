"""
Website B — Spoof SIMULATION of PixelVault Games.

This is an EDUCATIONAL demonstration, not a working phishing page:
  - It carries a (subtle) simulation notice on every page.
  - Its forms do NOT authenticate against the legit site's database.
  - When a mock login/signup is submitted, the submitted password is read into a
    local variable and immediately discarded. It is never written to a database,
    a log file, or the console.
  - Only a non-sensitive event (timestamp, method, origin, outcome) is recorded.
  - The form then simply rejects the attempt ("Invalid email or password."),
    exactly as a dead-end credential-collection page would appear to a visitor.
  - A calm /about page explains the difference between this look-alike and the
    real store.

It runs on a SEPARATE origin (127.0.0.1:5001) so you can show, in the browser,
that this is a different website from the real one.

Run:  python spoof_site/app.py   ->  http://127.0.0.1:5001
"""
import os
import secrets

from flask import Flask, render_template, request

import events

ORIGIN = "http://127.0.0.1:5001"
LEGIT_ORIGIN = "http://127.0.0.1:5000"

# A designated synthetic value used only as placeholder text on the forms.
DESIGNATED_DEMO_EMAIL = "participant@demo.test"

app = Flask(__name__)
app.config.update(SECRET_KEY=secrets.token_hex(16))

PRODUCT = {"title": "GTA VI", "price": "$69.99", "deal_price": "$19.99"}


@app.context_processor
def inject_globals():
    return {"origin_label": ORIGIN, "legit_origin": LEGIT_ORIGIN}


@app.route("/")
def index():
    return render_template("index.html", product=PRODUCT)


def _discard_and_log(outcome):
    """Read the submitted fields, discard the password immediately, and record
    only a non-sensitive event. No credential ever leaves this function."""
    _submitted_email = request.form.get("email", "")
    _submitted_password = request.form.get("password", "")
    del _submitted_password  # discarded immediately; nothing downstream sees it
    del _submitted_email
    events.record_event(method="POST", outcome=outcome)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Returning-user sign in (mock). Always rejects — it authenticates no one."""
    error = None
    if request.method == "POST":
        _discard_and_log("mock_login_submitted")
        error = "Invalid email or password."
    else:
        events.record_event(method="GET", outcome="viewed_login_form")
    return render_template("login.html", product=PRODUCT,
                           demo_email=DESIGNATED_DEMO_EMAIL, error=error)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """New-account creation (mock) — the discount hook. Always fails."""
    error = None
    if request.method == "POST":
        _discard_and_log("mock_signup_submitted")
        error = "We couldn't create your account right now. Please try again."
    else:
        events.record_event(method="GET", outcome="viewed_signup_form")
    return render_template("signup.html", product=PRODUCT,
                           demo_email=DESIGNATED_DEMO_EMAIL, error=error)


@app.route("/about")
def about():
    """A calm, plain explanation of what this demonstration is."""
    return render_template("about.html", legit_origin=LEGIT_ORIGIN, origin=ORIGIN)


if __name__ == "__main__":
    events.init_events_db()
    app.run(host="127.0.0.1", port=5001, debug=False)
