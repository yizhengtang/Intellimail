#db.py
#Opens the SQLite connection and creates the events table if it does not exist.

import sqlite3
import os

#calendar.db lives in the same directory as this file.
DB_PATH = os.path.join(os.path.dirname(__file__), 'calendar.db')

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    #Return rows as dicts so callers can access columns by name.
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            title           TEXT NOT NULL,
            event_date      TEXT NOT NULL,
            event_time      TEXT,
            description     TEXT,
            provider        TEXT NOT NULL,
            source_email_id TEXT NOT NULL,
            sender_name     TEXT
        )
    ''')
    conn.commit()
    conn.close()
