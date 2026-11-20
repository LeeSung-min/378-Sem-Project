"""
Initialize the PixelVault (legit site) SQLite database and seed demo users.

Run once:  python legit_site/database.py

This demonstrates security concept #7 (why passwords are hashed): we call
generate_password_hash() so the database only ever holds a one-way hash,
never the actual password.
"""
import os
import sqlite3
from datetime import datetime, timezone

from werkzeug.security import generate_password_hash

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "pixelvault.db")
SCHEMA_PATH = os.path.join(HERE, "schema.sql")

# Fictional demo accounts. These are the only credentials that exist anywhere.
DEMO_USERS = [
    ("demo@pixelvault.test", "Demo-Pass-123"),
    ("student@pixelvault.test", "Beach-2026!"),
]


def init_db():
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    now = datetime.now(timezone.utc).isoformat()
    for email, password in DEMO_USERS:
        conn.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
            (email, generate_password_hash(password), now),
        )
    conn.commit()
    conn.close()
    print(f"Initialized {DB_PATH}")
    print("Seeded demo users:")
    for email, password in DEMO_USERS:
        print(f"  {email}  /  {password}")


if __name__ == "__main__":
    init_db()
