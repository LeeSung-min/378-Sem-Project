# Demo walkthrough (script for the presentation)

Target length: ~8 minutes of demo inside your 10–15 minute slot. Have all three
servers running and the dashboard open in a second tab before you start.

## Part 1 — The real store (≈2 min)

1. Open `http://127.0.0.1:5000` and the address bar.
2. Browse the catalog, open a game, **Add to cart** a couple of items — show the cart
   count update and the cart totals. Say: "This is real, session-backed state."
3. Go to **Login**. Sign in with `demo@pixelvault.test` / `Demo-Pass-123`.
4. Land on the protected **Account** page (your cart carried over). Say: "The server
   only shows this because it checked my session cookie."
5. If your browser offered to save the password, accept it. You'll use this in Part 3.
6. Open the **dashboard** tab (`:5002`) and show the new `success` row in the real
   authentication log. Note: no password column anywhere.

## Part 2 — The spoof (≈3 min)

1. Open `http://127.0.0.1:5001`. It looks like the same store. The only tell is the
   address bar — the origin is `:5001`, not `:5000`. (A small "About this
   demonstration" link sits in the footer for disclosure.)
2. Point out the **social-engineering** elements: the countdown timer, the "flash
   sale" price, the popup. Say: "These exist to rush you past your normal checks."
3. Click **Claim discount** → the signup page. Type any email and password, submit.
4. It just fails: "Invalid email or password." / a generic error. Say: "A real
   phishing page would behave exactly like this dead end — the difference is that a
   real one keeps what you typed. Ours discards it and logs only that a submission
   happened." (The **About this demonstration** link explains the spoof-vs-real point.)
5. **Proof-of-capture (DevTools) — the key beat.** Before submitting, press **F12** →
   **Network** tab → check **Preserve log**. Type a *throwaway* password (e.g.
   `Hunter2-demo`) and submit. Click the `login` request and show:
   - **Headers → Request URL:** `http://127.0.0.1:5001/login` — the fake origin.
   - **Payload (Form Data):** the password, in plain text.
   Say: "I never typed this into the real store, but the fake site received it anyway.
   That is the capture — a real phishing page would just keep it. We don't." (Use a
   fake password; DevTools shows it in the clear, which is also the point about plain
   HTTP.) See `docs/devtools_guide.md` for the full version.
6. Back on the **dashboard**, show the new row in the spoof log — and point out there
   is literally no column for an email or a password.

## Part 3 — The defenses that actually work (≈3 min)

This is the strongest part. Do it live.

1. **Password manager origin binding.** On the spoof login page (`:5001`), click the
   password field. Your saved PixelVault login (saved on `:5000`) is **not offered**.
   Say: "The password manager refuses to autofill because the origin is different.
   That silence is a warning sign a human can be trained to notice."
2. **The address bar.** Put the two tabs side by side. Same look, different origin.
3. **Hashing.** Open `legit_site/pixelvault.db` (or show a screenshot). The `users`
   table stores a `pbkdf2:sha256...` hash, not the password. Say: "Even if this DB
   leaked, the passwords aren't in it."
4. **Passkeys (talking point).** Explain that a passkey/WebAuthn credential is bound
   to the real origin by the browser, so on `:5001` it produces no valid signature —
   nothing for the user to hand over, nothing for a relay to forward.

## Closing line

"A spoof can copy the pixels perfectly. What it can't copy is the origin — and every
real defense that matters (password managers, passkeys, and user awareness of the
address bar) keys off the origin, not the look."
