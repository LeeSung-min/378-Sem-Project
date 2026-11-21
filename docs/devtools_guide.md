# Inspecting requests with Chrome DevTools

This supports concepts #3, #4, and #5 (how front-end and back-end communicate, how
GET/POST work, how Flask receives form submissions).

## Open DevTools

- Press **F12** (or right-click → **Inspect**).
- Click the **Network** tab.
- Check **Preserve log** so entries survive page navigations.

## Watch a legit login (POST)

1. With Network recording, submit the login form on `http://127.0.0.1:5000`.
2. Find the `login` request in the list. Click it.
3. **Headers** panel:
   - **Request URL:** `http://127.0.0.1:5000/login`
   - **Request Method:** `POST`
   - **Status Code:** `302` (redirect to `/account` on success)
4. **Payload** panel: you'll see the form fields (`email`, `password`, `_csrf`).
   This is the moment to explain: on the real site this travels to the real server
   over the connection; in production this must be **HTTPS** so it's encrypted in
   transit.
5. **Response Cookies / Application tab → Cookies:** show the `session` cookie. Note
   it is marked **HttpOnly** (JavaScript can't read it) and **SameSite=Lax**.

## Watch the spoof mock login (POST)

1. Switch to `http://127.0.0.1:5001`, submit the mock login.
2. Find the `login` request. Note the **Request URL host/port is `127.0.0.1:5001`** —
   a different origin from the real store. This is the single most important thing to
   point at.
3. The response renders the same form again with an "Invalid email or password."
   error (HTTP 200). No session cookie is set, because nothing authenticated.

## Compare origins quickly

In the DevTools **Console**, run on each tab:

```js
window.location.origin
```

- Legit tab → `http://127.0.0.1:5000`
- Spoof tab → `http://127.0.0.1:5001`

Say: "To a human these pages look identical. To the browser they are unrelated
websites, and that is exactly what a password manager and a passkey rely on."

## GET vs POST in one glance

- Navigating to a page (clicking a link) = **GET** (no body, visible in the URL).
- Submitting a login form = **POST** (fields in the request body, not the URL).

Both appear in the Network tab with their method labeled, so you can show the
difference directly.
