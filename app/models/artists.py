import sqlite3
from app.config.db_connect import get_db_connection

def get_artist_by_url(url: str) -> dict | None:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM artists WHERE url = ?", (url,))
        artist = cur.fetchone()
        return dict(artist) if artist else None


def insert_artist(url: str, artist_name: str) -> int:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO artists (url, a_name) VALUES (?, ?)", (url, artist_name))
        conn.commit()
        return cur.lastrowid