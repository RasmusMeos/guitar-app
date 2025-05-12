from app.config.db_connect import get_db_connection


def get_all_chords_with_user_selection(user_id: int) -> dict[str, list[dict]]:

    query = '''
        SELECT 
            chords.id,
            chords.chord,
            chords.category,
            CASE WHEN user_chords.user_id IS NOT NULL THEN 1 ELSE 0 END AS selected
        FROM chords
        LEFT JOIN user_chords ON chords.id = user_chords.chord_id AND user_chords.user_id = ?
        ORDER BY chords.id -- tagastame samas järjekorras, kui akordid andmebaasi sisestati
    '''
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, (user_id,))
        rows = cur.fetchall()

    chords_by_category: dict[str, list[dict]] = {}
    for chord_id, chord_name, category, selected in rows:
        if category not in chords_by_category:
            chords_by_category[category] = []
        chords_by_category[category].append({
            "id": chord_id,
            "chord": chord_name,
            "selected": bool(selected)
        })
    return chords_by_category


def update_user_chords(user_id: int, chord_ids: list[int]) -> None:
    with get_db_connection() as conn:
        cur = conn.cursor()

        # eemaldame eksisteerivad valikud
        cur.execute("DELETE FROM user_chords WHERE user_id = ?", (user_id,))

        # lisame uued valikud
        if chord_ids:
            cur.executemany(
                "INSERT INTO user_chords (user_id, chord_id) VALUES (?, ?)",
                [(user_id, chord_id) for chord_id in chord_ids]
            )

        conn.commit()

def get_user_known_chords(user_id: int) -> list[str]:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT chords.chord
                FROM chords
                INNER JOIN user_chords ON chords.id = user_chords.chord_id
                WHERE user_chords.user_id = ?
            ''', (user_id,))
            return [row[0] for row in cur.fetchall()]