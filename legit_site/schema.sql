-- PixelVault Games (legitimate site) schema
-- Note: passwords are NEVER stored in plaintext. Only a salted hash is stored.

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,      -- Werkzeug scrypt hash, not the password
    created_at    TEXT NOT NULL
);

-- Login attempts on the LEGIT site, for the dashboard.
-- We record the outcome, never the password.
DROP TABLE IF EXISTS login_events;
CREATE TABLE login_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TEXT NOT NULL,
    origin      TEXT NOT NULL,        -- e.g. http://127.0.0.1:5000
    method      TEXT NOT NULL,        -- GET / POST
    email_tried TEXT,                 -- username only; useful for the demo, not secret
    outcome     TEXT NOT NULL         -- success / invalid_credentials
);
