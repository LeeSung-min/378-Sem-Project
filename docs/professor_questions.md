# Anticipated professor questions (with accurate answers)

**Q: Where are passwords stored, and in what form?**
On the legit site, in `pixelvault.db`, table `users`, column `password_hash`. It's a
Werkzeug salted `scrypt` hash (Werkzeug 3.x's default) — a one-way function. We never store or log the
plaintext. The spoof site stores no passwords at all; its event logger has no column
for one.

**Q: Show me that the spoof doesn't capture credentials.**
Open `spoof_site/events.py` — the `record_event()` function only accepts `method` and
`outcome`; there is no parameter for a password. In `spoof_site/app.py`, the login
handler reads the password into a local variable and `del`etes it immediately before
logging. We also ran a test asserting the submitted password never appears in the
events DB.

**Q: What exactly is the "origin," and why does it matter?**
Origin = scheme + host + port (e.g. `http://127.0.0.1:5000`). The browser isolates
sites by origin. Password managers save/autofill per origin, and passkeys bind their
keys to an origin. A spoof can copy the HTML but runs on a different origin, so those
origin-bound defenses don't carry over to it.

**Q: Why doesn't HTTPS prevent phishing?**
HTTPS/TLS secures the connection to whatever domain is in the address bar and proves
you're really talking to *that* domain. It says nothing about whether that domain is
the legitimate business. A phishing site can obtain a valid certificate for its own
look-alike domain, so the padlock is not proof of legitimacy.

**Q: How does the session work?**
On successful login, Flask stores `user_email` in its session, serialized into a
signed cookie (signed with `SECRET_KEY`). The browser returns the cookie on later
requests; `/account` checks it. The cookie is `HttpOnly` (JS can't read it) and
`SameSite=Lax`. Tampering breaks the signature, so the server rejects it.

**Q: What is the CSRF token for?**
It stops another site from submitting our forms on a logged-in user's behalf. Each
session gets a random token embedded in every POST form; the server rejects any POST
whose token doesn't match the session (returns HTTP 400).

**Q: Difference between phishing and spoofing?**
Spoofing is building the fake site; phishing is the delivery mechanism (email, text,
ad) that lures victims to it. We built a spoofed site for study and intentionally did
not create or send any lure, since that would be a real attack on real people.

**Q: Could this be used maliciously?**
Not as built. It has no credential capture, runs only on localhost, carries a visible
educational notice (and an About page), and uses fictional branding. To be an attack it would need credential storage/relay, a
convincing real-brand clone, a lure, and public deployment — all of which we
deliberately left out (and which the assignment forbids without written permission).

**Q: How would a real attacker defeat MFA, and what stops them?**
An adversary-in-the-middle phishing kit relays the victim's one-time code to the real
site in real time and steals the resulting session token. SMS and authenticator codes
are phishable this way. Passkeys/WebAuthn are not, because the credential is bound to
the real origin and won't produce a valid signature on the look-alike.

**Q: What did you each do?**
(Fill in per the assignment's team-contribution requirement — e.g. project manager,
lead coder for the legit site, lead coder for the spoof + dashboard, report/writer,
presenter.)

**Q: What would you add with more time?**
A WebAuthn/passkey login on the legit site to demonstrate the failure on the spoof
origin live; rate limiting and account lockout; and an HTTPS setup with self-signed
certs to show the padlock-is-not-legitimacy point directly.
