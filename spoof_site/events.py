"""
Non-sensitive event logging for the SPOOF simulation site.

Design decision that matters for the project: this logger has NO parameter and
NO database column for a password. The only things recorded are metadata that
prove "a mock submission reached this origin":

    ts, origin, method, outcome

There is deliberately no way to pass a submitted password into this function,
so the spoof site cannot store one even by accident. That is the difference
between a teaching demo and a phishing kit.
"""
import os
import sqlite3
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "spoof_events.db")
ORIGIN = "http://127.0.0.1:5001"


def init_events_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS mock_events (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            ts      TEXT NOT NULL,
            origin  TEXT NOT NULL,
            method  TEXT NOT NULL,
            outcome TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def record_event(method, outcome):
    """Record that an event happened. No credential data is accepted here."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO mock_events (ts, origin, method, outcome) VALUES (?, ?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), ORIGIN, method, outcome),
    )
    conn.commit()
    conn.close()


def all_events():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT ts, origin, method, outcome FROM mock_events ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
