# Security comparison of the two sites

| Property | Website A — Legit (`:5000`) | Website B — Spoof (`:5001`) |
|---|---|---|
| Real user database | Yes — `users` table with hashes | No |
| Validates credentials | Yes (`check_password_hash`) | No — nothing is validated |
| Stores submitted passwords | No — only a one-way hash at registration | No — password discarded on arrival |
| Issues an authenticated session | Yes, on success (signed cookie) | Never |
| CSRF protection on POST | Yes (per-session token) | N/A (no real state to protect) |
| Session cookie flags | HttpOnly, SameSite=Lax | N/A |
| Password-manager autofill | Yes — bound to its own origin | No — different origin, no offer |
| Social-engineering pressure | None | Countdown, flash discount, popup |
| What it logs | outcome + email tried (not secret) | only ts/origin/method/outcome |

## The core idea

A **spoof copies the front-end, never the back-end.** The visible page can be a
pixel-perfect clone. What it cannot clone is the **origin**, and every meaningful
defense keys off the origin:

- **Password managers** save and autofill credentials per origin. On a look-alike
  origin they stay silent — a built-in warning.
- **Passkeys / WebAuthn** sign a challenge that is cryptographically bound to the
  real origin. On a look-alike origin the signature is invalid, so there is nothing
  for a user to leak and nothing for an attacker-in-the-middle to relay. This is why
  passkeys are called *phishing-resistant* while SMS and authenticator-app codes are
  not.
- **HTTPS/TLS** proves you have a private, authentic connection to *whatever domain
  is in the address bar* — it does **not** prove that domain is the business you
  think it is. A phishing site can have a valid certificate for its own look-alike
  domain. (Concept #10.)

## Phishing vs. website spoofing (concept #2)

- **Website spoofing** = building the fake site that imitates a real one.
- **Phishing** = the delivery: the email, text, ad, or message that lures a victim to
  that fake site.

They usually appear together: phishing is the bait, the spoofed site is the trap.
In this project we built a spoofed site for study and deliberately did **not** build
or send any lure, because a live lure aimed at real people is an actual attack.

## Defenses, summarized for the report

1. Check the address bar / origin before entering anything.
2. Let a password manager fill credentials — if it won't, stop.
3. Prefer passkeys over passwords + OTP where available.
4. Treat urgency and "exclusive" offers as pressure tactics, not reasons to hurry.
5. On the server side: hash passwords, set HttpOnly/SameSite cookies, use CSRF
   tokens, and serve over HTTPS.
