"""
Website B — Spoof SIMULATION of PixelVault Games.

This is an EDUCATIONAL demonstration, not a working phishing page:
  - It carries a visible simulation notice on every page.
  - Its login form does NOT authenticate against the legit site's database.
  - When a mock login is submitted, the submitted password is read into a local
    variable and immediately discarded. It is never written to a database, a log
    file, or the console.
  - Only a non-sensitive event (timestamp, method, origin, outcome) is recorded.
  - The user is then shown an educational "reveal" explaining what just happened.

It runs on a SEPARATE origin (127.0.0.1:5001) so you can show, in the browser,
that this is a different website from the real one.

Run:  python spoof_site/app.py   ->  http://127.0.0.1:5001
"""
import os
import secrets

from flask import Flask, render_template, request, redirect, url_for

import events

ORIGIN = "http://127.0.0.1:5001"
LEGIT_ORIGIN = "http://127.0.0.1:5000"

# The single designated synthetic value the demo "expects". Using anything else
# still just triggers the educational reveal — nothing is validated for real.
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


def _handle_mock_submit(outcome):
    """Shared handling for both the mock login and mock signup forms.

    Reads the fields into locals ONLY so the reveal can say what happened, then
    discards the password immediately. The password is never persisted, logged,
    or printed. Returns the email-matched flag for the reveal.
    """
    _submitted_email = request.form.get("email", "")
    _submitted_password = request.form.get("password", "")
    del _submitted_password  # discarded immediately; nothing downstream sees it

    events.record_event(method="POST", outcome=outcome)
    return _submitted_email.strip().lower() == DESIGNATED_DEMO_EMAIL


@app.route("/login", methods=["GET", "POST"])
def login():
    """Returning-user sign in (mock)."""
    if request.method == "POST":
        matched = _handle_mock_submit("mock_login_submitted")
        return redirect(url_for("reveal", m=1 if matched else 0))

    events.record_event(method="GET", outcome="viewed_login_form")
    return render_template("login.html", product=PRODUCT,
                           demo_email=DESIGNATED_DEMO_EMAIL)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """New-account creation (mock) — the discount hook."""
    if request.method == "POST":
        matched = _handle_mock_submit("mock_signup_submitted")
        return redirect(url_for("reveal", m=1 if matched else 0))

    events.record_event(method="GET", outcome="viewed_signup_form")
    return render_template("signup.html", product=PRODUCT,
                           demo_email=DESIGNATED_DEMO_EMAIL)


@app.route("/reveal")
def reveal():
    matched = request.args.get("m") == "1"
    return render_template("reveal.html", matched=matched,
                           legit_origin=LEGIT_ORIGIN, origin=ORIGIN)


if __name__ == "__main__":
    events.init_events_db()
    app.run(host="127.0.0.1", port=5001, debug=True)
