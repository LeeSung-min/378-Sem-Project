# Demo walkthrough (script for the presentation)

Target length: ~8 minutes of demo inside your 10–15 minute slot. Have all three
servers running and the dashboard open in a second tab before you start.

## Part 1 — The real store (≈2 min)

1. Open `http://127.0.0.1:5000`. Point out the green "Real site" ribbon and the
   address bar.
2. Go to **Login**. Sign in with `demo@pixelvault.test` / `Demo-Pass-123`.
3. Land on the protected **Account** page. Say: "The server only shows this because
   it checked my session cookie."
4. If your browser offered to save the password, accept it. You'll use this in Part 3.
5. Open the **dashboard** tab (`:5002`) and show the new `success` row under
   "Legit login events." Note: no password column anywhere.

## Part 2 — The spoof (≈3 min)

1. Open `http://127.0.0.1:5001`. Keep the educational banner visible, but focus the
   audience on how similar the store looks.
2. Point out the **social-engineering** elements: the countdown timer, the "flash
   sale" price, the popup. Say: "These exist to rush you past your normal checks."
3. Click **Claim discount** → the mock login page.
4. Type the demo email `participant@demo.test` and any password. Submit.
5. The **reveal** page appears. Walk through it: the submission hit `:5001`, the
   password was discarded, only a non-sensitive event was logged.
6. Back on the **dashboard**, show the new "Spoof simulation events" row — and point
   out there is literally no column for an email or a password.

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
