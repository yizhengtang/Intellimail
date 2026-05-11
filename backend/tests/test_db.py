#test_db.py
#Unit tests for database/db.py — verifies that init_db() creates the correct schema,
#the migration is idempotent, and existing databases missing sender_name are upgraded safely.

import sqlite3
import pytest
import db


#get_db

def test_get_db_returns_sqlite_connection(tmp_path, monkeypatch):
    monkeypatch.setattr(db, 'DB_PATH', str(tmp_path / 'test.db'))
    conn = db.get_db()
    assert isinstance(conn, sqlite3.Connection)
    conn.close()


def test_get_db_uses_row_factory(tmp_path, monkeypatch):
    monkeypatch.setattr(db, 'DB_PATH', str(tmp_path / 'test.db'))
    conn = db.get_db()
    assert conn.row_factory == sqlite3.Row
    conn.close()


#init_db — table creation

def test_init_db_creates_events_table(tmp_path, monkeypatch):
    monkeypatch.setattr(db, 'DB_PATH', str(tmp_path / 'test.db'))
    db.init_db()
    conn = sqlite3.connect(str(tmp_path / 'test.db'))
    row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'").fetchone()
    assert row is not None
    conn.close()


def test_init_db_creates_all_required_columns(tmp_path, monkeypatch):
    monkeypatch.setattr(db, 'DB_PATH', str(tmp_path / 'test.db'))
    db.init_db()
    conn = sqlite3.connect(str(tmp_path / 'test.db'))
    columns = [row[1] for row in conn.execute('PRAGMA table_info(events)').fetchall()]
    conn.close()
    for expected in ['id', 'title', 'event_date', 'event_time', 'description', 'provider', 'source_email_id', 'sender_name']:
        assert expected in columns


#init_db — idempotency

def test_init_db_is_safe_to_call_twice(tmp_path, monkeypatch):
    monkeypatch.setattr(db, 'DB_PATH', str(tmp_path / 'test.db'))
    db.init_db()
    #Second call should not raise even though the column already exists.
    db.init_db()


#init_db — migration for existing databases

def test_init_db_adds_sender_name_to_existing_database(tmp_path, monkeypatch):
    db_path = str(tmp_path / 'old.db')
    monkeypatch.setattr(db, 'DB_PATH', db_path)

    #Create a database that mirrors the original schema without sender_name.
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE events (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            title           TEXT NOT NULL,
            event_date      TEXT NOT NULL,
            event_time      TEXT,
            description     TEXT,
            provider        TEXT NOT NULL,
            source_email_id TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

    #init_db should add the missing column without raising.
    db.init_db()

    conn = sqlite3.connect(db_path)
    columns = [row[1] for row in conn.execute('PRAGMA table_info(events)').fetchall()]
    conn.close()
    assert 'sender_name' in columns


#Basic insert and select to verify the schema accepts real data

def test_init_db_schema_accepts_event_insert(tmp_path, monkeypatch):
    monkeypatch.setattr(db, 'DB_PATH', str(tmp_path / 'test.db'))
    db.init_db()
    conn = db.get_db()
    conn.execute(
        'INSERT INTO events (title, event_date, provider, source_email_id, sender_name) VALUES (?, ?, ?, ?, ?)',
        ('Team Meeting', '2025-05-01', 'gmail', 'msg_abc', 'Alice')
    )
    conn.commit()
    row = conn.execute('SELECT * FROM events WHERE title = ?', ('Team Meeting',)).fetchone()
    assert row['title'] == 'Team Meeting'
    assert row['sender_name'] == 'Alice'
    conn.close()
