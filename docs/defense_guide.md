# Project Defense & Deep-Dive Guide

Everything in your project, explained from the bottom up, plus the questions a
professor is likely to ask and how to answer them. If you understand this
document, you can defend the project — that is the whole point.

---

## 0. Mindset for the Q&A

- **Understanding beats memorizing.** If you can *trace one login request end to
  end*, you can answer 80% of what they'll ask. Section 3 is that trace. Learn it
  cold.
- **If you don't know something, reason out loud from fundamentals.** Professors
  reward "I'm not 100% sure, but it must be X because Y" far more than a confident
  wrong answer or a blank stare.
- **Point at the code.** Having the files open and saying "right here on this line"
  is the strongest possible signal that you understand it. Section 9 maps concepts
  to files.
- **If asked directly how you built it / whether you used AI tools:** answer
  honestly according to your course's policy. The reliable move is to *demonstrate
  understanding* — that is what they're actually testing. This guide exists to make
  that understanding real.

---

## 1. The 30-second overview (your opening line)

"This project demonstrates website spoofing. There are three small web apps running
locally on different ports: a real game store with proper login, a visual look-alike
of it that collects nothing, and a dashboard that compares the two. The core lesson
is that a spoof can copy how a site *looks* perfectly, but it can't copy the site's
*origin* — the address in the browser — and every real defense against phishing keys
off that origin, not the appearance."

The three apps:
- **Legit store** — `http://127.0.0.1:5000` — real registration/login, hashed
  passwords, sessions, a working cart.
- **Spoof** — `http://127.0.0.1:5001` — looks the same, but authenticates no one and
  stores nothing.
- **Dashboard** — `http://127.0.0.1:5002` — shows events from both side by side.

---

## 2. The big mental model: client, server, request/response

A website is two computers talking:
- The **client** = your web browser.
- The **server** = our Flask program.

They talk over **HTTP**. The browser sends a **request**; the server sends back a
**response** (usually an HTML page). Every page load and every form submit is one
request/response round trip.

Two request types matter here:
- **GET** — "give me this page." No body; any data rides in the URL. Clicking a link
  = GET.
- **POST** — "here's some data, do something with it." The data (like your email and
  password) rides in the **body** of the request, not the URL. Submitting a form =
  POST.

**Flask** is the Python library that is our server. It listens on a port, matches the
request's URL to a Python function (a "route"), runs it, and returns the response.

---

## 3. THE trace: what happens when you click "Sign in" on the real site

This is the single most important thing to know. Memorize the flow; say it in your
own words.

1. You visit `http://127.0.0.1:5000/login`. The browser sends a **GET** request.
   Flask matches it to the `login()` function, which renders `login.html` and sends
   the HTML back. You see the form.
2. You type your email and password and click Sign in. The browser bundles the form
   fields into a **POST** request to `/login` and sends them in the request body.
3. Flask's `csrf_protect()` runs first (it's a `before_request` hook). It checks that
   the form's hidden `_csrf` token matches the one stored in your session. If not, it
   rejects the request with HTTP 400. (Defends against CSRF — see 4.6.)
4. The `login()` function runs. It reads the email, then asks **SQLite**: "give me
   the user row with this email."
5. It calls `check_password_hash(stored_hash, typed_password)`. This re-hashes what
   you typed and compares it to the stored hash. **The real password is never stored
   or compared directly** — only hashes are compared.
6. **If they match:** Flask stores `user_email` in the **session** and sends back a
   redirect to `/account`, along with a `Set-Cookie` header containing the signed
   session cookie. The browser saves that cookie.
7. **If they don't match:** it re-renders the login page with "Invalid email or
   password."
8. Now you request `/account`. The browser automatically includes the session cookie.
   The `account()` function checks "is `user_email` in the session?" Yes → it shows
   the protected page. (If you had no valid cookie, it would redirect you to login.)

Every login attempt also gets logged (time, method, email tried, outcome) to a
`login_events` table so the dashboard can show it. **The password is never in that
log.**

---

## 4. Component deep dives (bottom up)

### 4.1 HTTP status codes you'll see
- **200 OK** — here's your page.
- **302 Found** — redirect ("go here instead"); used after a successful login to send
  you to `/account`.
- **400 Bad Request** — we used it when the CSRF token is missing/wrong.
- **404 Not Found** — e.g. a product slug that doesn't exist.

### 4.2 Flask: routes and templates
- A **route** is a URL pattern tied to a function: `@app.route("/login")`.
- `render_template("login.html", ...)` fills an HTML template with data and returns
  it. Templates use **Jinja2** — the `{{ ... }}` and `{% ... %}` you see in the HTML
  files. `{{ game.title }}` inserts a value; `{% for game in catalog %}` loops.
- Templates share a **base.html** via `{% extends %}` so the nav/footer are written
  once.

### 4.3 SQLite and the schema
- **SQLite** is a tiny database that lives in a single file (`pixelvault.db`). No
  server to install — good for a demo.
- Our `users` table has: `id`, `email`, `password_hash`, `created_at`. **Note what's
  *not* there: no `password` column.** We only ever store the hash.
- `database.py` creates the table and seeds two demo accounts. We use **parameterized
  queries** (the `?` placeholders) everywhere, which prevents **SQL injection** — the
  user's input can never be interpreted as SQL commands.

### 4.4 Password hashing — the big one
- **Why not store the password as-is?** If the database ever leaks, every password is
  exposed — and people reuse passwords everywhere. So you must not keep the plaintext.
- **Hashing** runs the password through a one-way function. You can compute the hash
  from the password, but you **cannot reverse** the hash back to the password.
- At signup we call `generate_password_hash(password)` (Werkzeug). It produces a
  string like `scrypt:32768:8:1$abc123$def456...` which encodes: the algorithm
  (**scrypt**, Werkzeug 3.x's default), its **cost settings** (N=32768, r=8, p=1), a
  random **salt**, and the resulting hash.
- At login we call `check_password_hash(stored, typed)`. It pulls the salt and
  settings out of the stored string, re-hashes what you typed the same way, and
  compares. Match → correct password.
- **Salt** = random bytes mixed in per password. It means two users with the same
  password get different hashes, and it defeats precomputed "rainbow table" attacks.
- **Cost settings** make each guess slow, and scrypt is also **memory-hard** (each
  guess needs a lot of RAM), so brute-forcing the hashes on GPUs is expensive.

> **Hashing vs. encryption** (a classic question): Encryption is *two-way* — with the
> key you can decrypt back to the original. Hashing is *one-way* — there's no key and
> no way back. You use hashing for passwords because you never need to recover the
> password, only verify it. One-way is safer: a breach reveals hashes, not passwords.

### 4.5 Sessions and cookies
- **HTTP is stateless** — the server forgets you between requests. A **session** is
  how it remembers you're logged in.
- After login we put `user_email` in Flask's `session`. Flask serializes that into a
  **cookie** and sends it to the browser; the browser returns it on every later
  request, so the server knows who you are.
- The cookie is **signed** with our `SECRET_KEY` (using HMAC). Signed means
  **tamper-evident**: if you edit the cookie, the signature breaks and Flask rejects
  it. (Important nuance: signed ≠ encrypted. By default the contents are readable —
  base64 — but not forgeable. Don't put secrets in a Flask session.)
- Cookie flags we set:
  - **HttpOnly** — JavaScript can't read the cookie, which blocks a whole class of
    cookie-theft via XSS.
  - **SameSite=Lax** — the browser won't send the cookie on most cross-site requests,
    which blunts CSRF.
  - **Secure** — the cookie is only sent over HTTPS. We set this *adaptively*: off on
    the plain-HTTP localhost demo (so login works), on automatically when served over
    HTTPS. (That's the `AdaptiveSessionInterface` class.)
- `SECRET_KEY` signs the cookie. If it changes, all existing cookies become invalid
  (everyone's logged out). We read it from an environment variable with a fixed local
  fallback so the demo's sessions survive restarts.

### 4.6 CSRF (Cross-Site Request Forgery)
- **The attack:** you're logged into our site. You visit a malicious page. It
  silently submits a form to *our* site using your logged-in cookie, doing something
  as you (e.g. a state change) without your intent.
- **The defense:** every form includes a secret per-session token in a hidden field.
  On every POST, the server checks the submitted token against the session's token. A
  malicious page can't know your token, so its forged request fails. That's the
  `csrf_protect()` hook (returns 400 on mismatch).
- Ours is a minimal hand-rolled version of what the Flask-WTF library does.

### 4.7 The cart (session-backed state)
- The cart is stored **in the session** as `{slug: quantity}`. Add/remove/clear are
  POST routes that update it. Totals are computed from the catalog prices at render
  time. It persists across login because we copy it over when the session resets.

### 4.8 The spoof — how it looks real but captures nothing
- It's a separate Flask app on **port 5001 — a different origin.**
- Its login/signup forms POST to **itself** (`:5001`), not the real store.
- The handler reads the email and password into local variables, then **immediately
  `del`etes them** — they are never written to a database, a log, or the console.
- It records only a non-sensitive **event** (time, method, origin, outcome). Look at
  `events.py`: the logging function has **no parameter for a password** — so it
  *can't* store one even by mistake.
- It then just returns "Invalid email or password." — it authenticates no one.
- **Why build it this way?** The teaching point is the *attack flow*, not hoarding
  secrets. We prove capture live in DevTools (the password sitting in the POST body
  going to `:5001`) without creating a real credential store. That's responsible
  data-minimization — a good thing to say.

### 4.9 Dashboard + timezone
- Reads both databases read-only and shows counts (including "passwords the spoof
  stored: 0"), a comparison table, and live event feeds.
- Timestamps are stored in **UTC** and converted to **Pacific** for display
  (`America/Los_Angeles`, so DST is automatic). On Windows the IANA tz database isn't
  bundled, so we fall back to a fixed −8 offset if the `tzdata` package isn't
  installed.

---

## 5. The security concepts from your brief — one tight answer each

- **What is website spoofing?** Building a site that imitates a real one to deceive
  users.
- **Spoofing vs. phishing?** Spoofing is the fake *site*; phishing is the *delivery*
  (the email/text/ad that lures you there). They usually come together.
- **How do front end and back end communicate?** Over HTTP — the browser sends
  requests, the Flask server sends responses.
- **GET vs POST?** GET fetches a page (data in the URL); POST submits data (in the
  request body).
- **How does Flask handle a form?** A route with `methods=["POST"]` reads
  `request.form`, processes it, and returns a response.
- **How does SQLite store accounts?** In a `users` table, with the password kept only
  as a hash.
- **Why hash passwords?** So a database leak doesn't expose real passwords; hashing is
  one-way.
- **How do sessions work?** A signed cookie holds who you are; the browser returns it
  each request so the stateless server remembers you.
- **How do password managers associate credentials with a site?** By **origin**. They
  only offer a saved login on the exact site where you saved it — so they stay silent
  on a look-alike.
- **Why don't HTTPS/certs prove legitimacy?** A certificate proves you have an
  encrypted connection to *whatever domain is in the bar* and that whoever got the
  cert controls that domain — not that the domain is the real company. Certs are free
  and automatic (Let's Encrypt), so the padlock guarantees encryption, not identity.
- **How do domains/origins tell sites apart?** The **origin** = scheme + host + port.
  `127.0.0.1:5000` and `127.0.0.1:5001` are different origins — different websites to
  the browser.
- **How does social engineering work here?** Urgency (countdown), scarcity
  ("limited-time"), and a reward (discount popup) pressure you to act before you
  check the address bar.

---

## 6. Why we made these design choices (defending your decisions)

- **Why no credential capture in the spoof?** It adds no teaching value over showing
  the capture live in DevTools, and it would create a real credential store — a
  liability. Data minimization is itself good security practice.
- **Why localhost only?** It's a controlled environment; a public look-alike login
  page is the kind of thing that gets flagged as phishing. The assignment also
  forbids deploying an attack without written permission.
- **Why a fictional store (PixelVault)?** So we're not impersonating a real company.
- **Why Flask + SQLite?** Minimal, readable, standard for teaching — no heavyweight
  frameworks hiding what's happening.
- **Why three separate apps/ports?** So the **origin difference** is real and
  demonstrable in the browser — that's the core lesson.
- **Why not deploy with HTTPS?** The "cert ≠ legitimacy" point is proven by how
  trivially anyone gets a free cert, plus real phishing-with-padlock examples;
  deploying our own adds risk without adding a concept.

---

## 7. Anticipated professor questions, by angle

### A. Tracing ("walk me through…")
- **"What happens when I click Sign in?"** → Give the Section 3 trace.
- **"What happens when I add something to the cart?"** → POST to `/cart/add` with the
  slug and CSRF token → the route updates the `{slug: qty}` dict in my session →
  redirect to `/cart`, which computes totals from the catalog.
- **"What happens when I submit the spoof login?"** → POST to `:5001` → it reads and
  immediately discards the password, logs only an event, and returns an "invalid"
  error. Nothing is stored or authenticated.

### B. Design ("why did you… / why not…")
- **"Why scrypt and not just SHA-256?"** → A plain fast hash is brute-forceable.
  scrypt adds a salt and is deliberately slow and memory-hard, so each guess is
  expensive and rainbow tables don't work. (Older Werkzeug versions used PBKDF2;
  3.x defaults to scrypt.)
- **"Why store a hash and not encrypt the password?"** → You never need to recover a
  password, only verify it; one-way hashing means a breach doesn't reveal passwords.
- **"Why SameSite/HttpOnly on the cookie?"** → HttpOnly blocks JS cookie theft (XSS);
  SameSite blunts CSRF.

### C. Code location ("show me where…")
- Have the files open. See Section 9 for exact spots.

### D. Critique ("what's the weakness / what would you improve?")
- Be honest and specific, it shows maturity:
  - No rate limiting or account lockout on login → brute-force possible. Would add it.
  - CSRF protection is hand-rolled and minimal → would use Flask-WTF in production.
  - No HTTPS in the demo → fine for localhost, required in production.
  - Passkeys are discussed, not implemented → would add WebAuthn to show the
    phishing-resistant login live.
  - `debug` and secret handling are demo-grade → real deployment needs a managed
    secret and `debug=False` (we do set it False).

### E. "What if…" (edge cases / attacks)
- **"What if I steal your session cookie?"** → You could impersonate me until it
  expires — "session hijacking." That's why HttpOnly (stops JS theft) and HTTPS
  (stops network sniffing) matter.
- **"What if I tamper with the cookie?"** → The HMAC signature breaks and Flask
  rejects it.
- **"What if the spoof pointed its form at the real site?"** → Then it'd be a
  real-time relay / adversary-in-the-middle — that's how advanced kits steal sessions
  and defeat OTP MFA. We deliberately don't build that.

### F. Conceptual security
- **"What's a salt?"** → Random per-password data mixed into the hash so identical
  passwords hash differently and rainbow tables don't work.
- **"Signed vs encrypted cookie?"** → Signed = tamper-proof but readable; encrypted =
  also unreadable. Flask sessions are signed by default.
- **"Does HTTPS stop phishing?"** → No. It secures the connection to the shown domain;
  it doesn't tell you the domain is the real business.
- **"How does a passkey resist phishing?"** → It's cryptographically bound to the real
  site's origin; on a look-alike it produces no valid signature, and there's nothing
  the user can type and hand over.

### G. Gotchas
- **"Is this a real phishing attack?"** → No — it runs locally, uses a fictional
  brand, captures nothing, and self-discloses via an About page. To be a real attack
  it would need credential storage/relay, a real-brand clone, a lure, and public
  deployment — all deliberately absent.
- **"Could someone actually get hacked by this?"** → No; it stores nothing and
  reaches no real users.

---

## 8. Honest caveats — things that could go sideways in the live demo

Know these so a surprise doesn't rattle you:

- **The password manager might still autofill on the spoof.** The real-world defense
  is that a manager binds a saved login to its **domain**, so on a different domain
  (e.g. `paypa1.com`) it won't autofill. Our spoof differs only by **port** on the
  same host (`127.0.0.1`), and some password managers match by hostname and ignore
  the port — so they *might* offer the saved login on `:5001`. If that happens, say:
  "On localhost the sites differ only by port; a real attack uses a different domain,
  where the manager definitely wouldn't autofill — that domain binding is the point."
  This turns a glitch into a teaching moment.
- **Passkeys are a talking point, not implemented.** Don't claim the project has a
  working passkey login; say it's the natural next step and explain why it resists
  spoofing.
- **DevTools shows the password in plain text.** That's intentional (it's the capture,
  and it's plain HTTP) — use a throwaway password, and make the plain-text visibility
  your point about why HTTPS matters in transit.
- **The spoof's "flash sale" and popup are deliberate.** If asked, they demonstrate
  social-engineering pressure tactics; they aren't filler.

---

## 9. Have these open during the demo (concept → file)

- Password hashing → `legit_site/app.py` (`generate_password_hash` in `register`,
  `check_password_hash` in `login`) and `legit_site/database.py`.
- Schema / no password column → `legit_site/schema.sql`.
- Sessions + cookie flags + adaptive Secure → `legit_site/app.py`
  (`app.config`, `AdaptiveSessionInterface`).
- CSRF → `legit_site/app.py` (`csrf_token`, `csrf_protect`).
- Spoof discards credentials → `spoof_site/app.py` (`_discard_and_log`) and
  `spoof_site/events.py` (no password field).
- Origin difference → the three `app.run(... port=5000/5001/5002)` lines.
- Dashboard "0 stored" + comparison → `dashboard/app.py`, `dashboard/templates/dashboard.html`.

---

## 10. If you get stuck in Q&A

- "Let me trace that from the top…" then walk the request flow — it usually contains
  the answer.
- "I'm not certain of the exact detail, but the principle is… because…" — reason from
  fundamentals.
- "That's a good improvement — in production I'd add…" — turn a gap into a
  forward-looking answer.
- It's fine to point at the code and read it with them; that *demonstrates* ownership.
