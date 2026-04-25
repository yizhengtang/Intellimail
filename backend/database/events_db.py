#events_db.py
#CRUD functions for the events table in calendar.db.

from database.db import get_db

#Inserts one event row and returns the new row ID.
def create_event(title: str, event_date: str, provider: str, source_email_id: str,
                 event_time: str = None, description: str = None) -> int:
    conn = get_db()
    cursor = conn.execute(
        '''INSERT INTO events (title, event_date, event_time, description, provider, source_email_id)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (title, event_date, event_time, description, provider, source_email_id)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

#Returns all events for a given year and month, sorted by date and time ascending.
#event_date is stored as YYYY-MM-DD so filtering with LIKE 'YYYY-MM-%' is safe and correct.
def get_events_by_month(year: int, month: int) -> list[dict]:
    prefix = f'{year}-{month:02d}'
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM events WHERE event_date LIKE ? ORDER BY event_date ASC, event_time ASC',
        (f'{prefix}-%',)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

#Deletes one event by ID. Returns True if a row was deleted, False if the ID did not exist.
def delete_event(event_id: int) -> bool:
    conn = get_db()
    cursor = conn.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted
