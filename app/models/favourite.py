from app.config.db_connect import get_db_connection
import sqlite3


def toggle_favourite_song(user_id: int, song_id: int) -> bool:
    with get_db_connection() as conn:
        cur = conn.cursor()

        # Kas on juba lemmikuks märgitud
        cur.execute("SELECT 1 FROM user_songs WHERE user_id = ? AND song_id = ?", (user_id,song_id))
        if cur.fetchone():
            cur.execute("DELETE FROM user_songs WHERE user_id = ? AND song_id = ?", (user_id, song_id))
            conn.commit()
            return False
        else:
            cur.execute("INSERT INTO user_songs (user_id, song_id) VALUES (?, ?)", (user_id, song_id))
            conn.commit()
            return True

def get_user_favourite_songs(user_id: int) -> list[dict] | None:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('''
            SELECT songs.*, artists.a_name as artist_name
            FROM songs
            JOIN user_songs ON songs.id = user_songs.song_id
            JOIN artists ON songs.artist_id = artists.id
            WHERE user_songs.user_id = ?
        ''', (user_id,))
        return [dict(row) for row in cur.fetchall()]

def get_user_favourite_song_ids(user_id: int) -> list[int]:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT song_id FROM user_songs WHERE user_id = ?', (user_id,))
        return [row[0] for row in cur.fetchall()]

def is_favourite(user_id: int, song_id: int) -> bool:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute('SELECT 1 FROM user_songs WHERE user_id = ? AND song_id = ?', (user_id, song_id))
        return cur.fetchone() is not None