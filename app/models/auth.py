import sqlite3
from app.config.db_connect import get_db_connection

def insert_user(username: str, hashed_pwd: str) -> int | None:
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_pwd)
        )
        conn.commit()
    return cur.lastrowid if cur.rowcount > 0 else None


def get_user_by_username(username: str) -> dict | None:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        return dict(user) if user else None