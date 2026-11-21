"""
Website A — PixelVault Games (LEGITIMATE store).

Demonstrates real, secure authentication plus a working storefront:
  - registration + login/logout
  - passwords hashed with Werkzeug (never stored in plaintext)
  - server-side session via Flask's signed session cookie
  - a protected /account page
  - a real, session-backed shopping cart (add / remove / clear)
  - CSRF protection on all POST forms
  - sensible session-cookie flags (HttpOnly, SameSite, and Secure when on HTTPS)

Run:  python legit_site/app.py   ->  http://127.0.0.1:5000
"""
import os
import secrets
import sqlite3
from datetime import datetime, timezone

from flask import (
    Flask, g, render_template, request, redirect, url_for, session, flash, abort
)
from flask.sessions import SecureCookieSessionInterface
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "pixelvault.db")
ORIGIN = "http://127.0.0.1:5000"

app = Flask(__name__)

# SECRET_KEY comes from the environment in production; a fixed local fallback
# keeps sessions stable across restarts during the demo.
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "local-dev-key-change-me"),
    SESSION_COOKIE_HTTPONLY=True,     # JS cannot read the session cookie
    SESSION_COOKIE_SAMESITE="Lax",    # limits cross-site cookie sending
    # NOTE: we intentionally do NOT set SESSION_COOKIE_SECURE here.
    # The adaptive session interface below decides it per request instead.
)

# If the app runs behind a reverse proxy that terminates TLS (nginx/Apache),
# trust its X-Forwarded-Proto header so request.is_secure reflects the real
# scheme the browser used. Harmless on localhost.
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


class AdaptiveSessionInterface(SecureCookieSessionInterface):
    """Set the session cookie's Secure flag based on the actual request.

    - Over plain HTTP (the localhost demo) the cookie is NOT marked Secure,
      so the browser stores and returns it and login persists.
    - Over HTTPS (a real deployment) the cookie IS marked Secure, so it is
      only ever sent over encrypted connections.

    This means the same code works in both cases with nothing to toggle.
    """
    def get_cookie_secure(self, app):
        return bool(request and request.is_secure)


app.session_interface = AdaptiveSessionInterface()

# ---------- product catalog ----------
# A small fixed catalog. Cover images are stored under static/img/.
# (Store brand "PixelVault Games" is fictional; the game titles/art are used as
# example product listings for a class demonstration.)
CATALOG = [
    {
        "slug": "gta-vi", "title": "GTA VI", "price": 69.99, "img": "gta-vi.png",
        "tagline": "The most anticipated open-world game returns to Vice City.",
        "description": "The next chapter in the open-world series. Example product "
                       "listing for a class demonstration — no real sale is processed.",
        "screens": ["Beachfront skyline", "Neon downtown", "Open highway"],
    },
    {
        "slug": "fortnite", "title": "Fortnite", "price": 0.00, "img": "fortnite.jpg",
        "tagline": "Drop in, build, and battle to be the last one standing.",
        "description": "Free-to-play battle royale. Example product listing for a class "
                       "demonstration.",
        "screens": ["The drop", "Final circle", "Victory"],
    },
    {
        "slug": "minecraft", "title": "Minecraft", "price": 29.99, "img": "minecraft.jpg",
        "tagline": "Build, explore, and survive in an infinite blocky world.",
        "description": "Sandbox survival and creativity. Example product listing for a "
                       "class demonstration.",
        "screens": ["First night", "Cherry grove", "The mines"],
    },
    {
        "slug": "pokemon-lets-go-pikachu", "title": "Pokémon: Let's Go, Pikachu!",
        "price": 59.99, "img": "pokemon.jpg",
        "tagline": "Catch, train, and travel the Kanto region with Pikachu.",
        "description": "Classic creature-collecting adventure. Example product listing "
                       "for a class demonstration.",
        "screens": ["Pallet Town", "Catching", "Gym battle"],
    },
    {
        "slug": "valorant", "title": "VALORANT", "price": 0.00, "img": "valorant.jpg",
        "tagline": "A 5v5 tactical shooter where precision meets abilities.",
        "description": "Free-to-play tactical shooter. Example product listing for a "
                       "class demonstration.",
        "screens": ["Spike plant", "Clutch round", "Ace"],
    },
    {
        "slug": "zelda-ocarina-of-time", "title": "The Legend of Zelda: Ocarina of Time",
        "price": 59.99, "img": "zelda.jpg",
        "tagline": "A timeless adventure through Hyrule, forest to castle.",
        "description": "Classic action-adventure. Example product listing for a class "
                       "demonstration.",
        "screens": ["Kokiri Forest", "Hyrule Field", "Temple of Time"],
    },
]
CATALOG_BY_SLUG = {g["slug"]: g for g in CATALOG}


# ---------- database helpers ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def log_login(method, email_tried, outcome):
    db = get_db()
    db.execute(
        "INSERT INTO login_events (ts, origin, method, email_tried, outcome) "
        "VALUES (?, ?, ?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), ORIGIN, method, email_tried, outcome),
    )
    db.commit()


# ---------- cart helpers (session-backed) ----------
def get_cart():
    """Return the cart dict {slug: qty} from the session."""
    return session.get("cart", {})


def cart_items():
    """Expand the cart into a list of line items with subtotals, plus the total."""
    cart = get_cart()
    items, total = [], 0.0
    for slug, qty in cart.items():
        game = CATALOG_BY_SLUG.get(slug)
        if not game:
            continue
        subtotal = game["price"] * qty
        total += subtotal
        items.append({"game": game, "qty": qty, "subtotal": subtotal})
    return items, total


def cart_count():
    return sum(get_cart().values())


# ---------- CSRF protection ----------
# A minimal per-session token. Every POST form includes it as a hidden field;
# the server rejects any POST whose token doesn't match the session.
def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(16)
    return session["_csrf"]


@app.before_request
def csrf_protect():
    if request.method == "POST":
        sent = request.form.get("_csrf", "")
        if not sent or sent != session.get("_csrf"):
            abort(400, "CSRF token missing or invalid.")


@app.context_processor
def inject_globals():
    return {
        "csrf_token": csrf_token,
        "current_user": session.get("user_email"),
        "origin_label": ORIGIN,
        "cart_count": cart_count(),
    }


# ---------- routes ----------
@app.route("/")
def index():
    return render_template("index.html", catalog=CATALOG, featured=CATALOG[0])


@app.route("/product/<slug>")
def product(slug):
    game = CATALOG_BY_SLUG.get(slug)
    if not game:
        abort(404)
    return render_template("product.html", product=game)


@app.route("/cart")
def cart():
    items, total = cart_items()
    return render_template("cart.html", items=items, total=total)


@app.route("/cart/add", methods=["POST"])
def cart_add():
    slug = request.form.get("slug", "")
    if slug not in CATALOG_BY_SLUG:
        abort(404)
    cart = dict(get_cart())
    cart[slug] = cart.get(slug, 0) + 1
    session["cart"] = cart
    flash(f"Added {CATALOG_BY_SLUG[slug]['title']} to your cart.", "ok")
    return redirect(url_for("cart"))


@app.route("/cart/remove", methods=["POST"])
def cart_remove():
    slug = request.form.get("slug", "")
    cart = dict(get_cart())
    if slug in cart:
        del cart[slug]
        session["cart"] = cart
        flash("Item removed.", "ok")
    return redirect(url_for("cart"))


@app.route("/cart/clear", methods=["POST"])
def cart_clear():
    session["cart"] = {}
    flash("Cart cleared.", "ok")
    return redirect(url_for("cart"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("register.html")
        if len(password) < 8:
            flash("Use at least 8 characters.", "error")
            return render_template("register.html")

        db = get_db()
        existing = db.execute(
            "SELECT id FROM users WHERE email = ?", (email,)
        ).fetchone()
        if existing:
            flash("An account with that email already exists.", "error")
            return render_template("register.html")

        db.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
            (email, generate_password_hash(password),
             datetime.now(timezone.utc).isoformat()),
        )
        db.commit()
        flash("Account created. You can log in now.", "ok")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

        # check_password_hash compares against the stored hash; the plaintext
        # password is never read from or written to the database.
        if user and check_password_hash(user["password_hash"], password):
            # Preserve the cart across the session reset on login.
            saved_cart = get_cart()
            session.clear()
            session["user_email"] = user["email"]
            session["cart"] = saved_cart
            csrf_token()  # refresh token for the new session
            log_login("POST", email, "success")
            flash("Signed in successfully.", "ok")
            return redirect(url_for("account"))

        log_login("POST", email, "invalid_credentials")
        flash("Invalid email or password.", "error")
        return render_template("login.html")

    log_login("GET", None, "viewed_form")
    return render_template("login.html")


@app.route("/account")
def account():
    if not session.get("user_email"):
        flash("Please sign in to view your account.", "error")
        return redirect(url_for("login"))
    items, total = cart_items()
    return render_template("account.html", email=session["user_email"],
                           items=items, total=total)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Signed out.", "ok")
    return redirect(url_for("index"))


if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("Database not found. Run:  python legit_site/database.py")
    app.run(host="127.0.0.1", port=5000, debug=False)
