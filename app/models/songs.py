import json
import sqlite3

from app.config.db_connect import get_db_connection


def insert_all_songs(song_links: list[str], artist_id: int) -> None:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.executemany(
            "INSERT OR IGNORE INTO songs (url, artist_id) VALUES (?, ?)",
            [(url, artist_id) for url in song_links]
        )
        conn.commit()


def get_random_songs_for_display(artist_id: int, limit: int) -> list[dict]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM songs
            WHERE artist_id = ?
            ORDER BY (tab IS NULL) DESC, RANDOM() -- loome suvalise järjestuse töötlemata lugude alusel
            LIMIT ? 
        ''', (artist_id, limit))
        return [dict(songs) for songs in cur.fetchall()]


def update_song(song_id: int, title: str, tab:str, chord_pos: str, in_key: str) -> dict | None:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
        UPDATE songs
        SET title = ?, tab = ?, chord_positions = ?, in_key = ?
        WHERE id = ?
        ''', (title, tab, chord_pos, in_key, song_id))
        conn.commit()

        if cur.rowcount == 0:
            return None

        return {
            "id": song_id,
            "title": title,
            "tab": tab,
            "chord_positions": json.loads(chord_pos),
            "in_key": in_key
        }

def get_song_by_id(song_id: int) -> dict | None:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
        song = cur.fetchone()
        return dict(song) if song else None


def delete_song(song_id: int) -> None:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM songs WHERE id = ?", (song_id,))
        conn.commit()

def update_song_yt_url(song_id: int, yt_url: str) -> None:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE songs SET yt_url = ? WHERE id = ?", (yt_url,song_id))
        conn.commit()







