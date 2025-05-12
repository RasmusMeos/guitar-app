import sqlite3
from app.config.db_connect import DB_PATH

def initialize_database():
    with sqlite3.connect(DB_PATH) as connection:
        c = connection.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS chords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chord TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL
            )
        ''')

        c.execute('''
         CREATE TABLE IF NOT EXISTS user_chords (
             user_id INTEGER,
             chord_id INTEGER,
             PRIMARY KEY (user_id, chord_id),
             FOREIGN KEY (user_id) REFERENCES users(id),
             FOREIGN KEY (chord_id) REFERENCES chords(id)
             )
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            a_name TEXT NOT NULL
            )
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            yt_url TEXT,
            title TEXT,
            tab TEXT,
            chord_positions TEXT,
            in_key TEXT,
            artist_id INTEGER,
            FOREIGN KEY (artist_id) REFERENCES artists(id)
            )
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS user_songs (
            user_id INTEGER,
            song_id INTEGER,
            PRIMARY KEY (user_id, song_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
            )
        ''')

        c.execute('SELECT COUNT(*) FROM chords')
        count = c.fetchone()[0]
        if count == 0:
            chords = [
                # mažoorid
                ("C", "major"), ("C#", "major"), ("D", "major"), ("D#", "major"), ("E", "major"), ("F", "major"),
                ("F#", "major"),("G", "major"),("G#", "major"),("A", "major"),("A#", "major"),("B", "major"),

                # minoorid
                ("Cm", "minor"), ("C#m", "minor"), ("Dm", "minor"), ("D#m", "minor"), ("Em", "minor"), ("Fm", "minor"),
                ("F#m", "minor"), ("Gm", "minor"), ("G#m", "minor"), ("Am", "minor"), ("A#m", "minor"), ("Bm", "minor"),

                # jõuakordid
                ("C5", "power"), ("C#5", "power"), ("D5", "power"), ("D#5", "power"), ("E5", "power"), ("F5", "power"),
                ("F#5", "power"), ("G5", "power"), ("G#5", "power"), ("A5", "power"), ("A#5", "power"), ("B5", "power"),

                # dominantseptakordid
                ("C7", "dom7th"), ("C#7", "dom7th"), ("D7", "dom7th"), ("D#7", "dom7th"), ("E7", "dom7th"), ("F7", "dom7th"),
                ("F#7", "dom7th"), ("G7", "dom7th"), ("G#7", "dom7th"), ("A7", "dom7th"), ("A#7", "dom7th"), ("B7", "dom7th"),

                # vähendatud kolmkõlad
                ("Cdim", "diminished"), ("C#dim", "diminished"), ("Ddim", "diminished"), ("D#dim", "diminished"), ("Edim", "diminished"), ("Fdim", "diminished"),
                ("F#dim", "diminished"), ("Gdim", "diminished"), ("G#dim", "diminished"), ("Adim", "diminished"), ("A#dim", "diminished"), ("Bdim", "diminished"),

                # populaarsemad "suspended" kitarriakordid
                ("Dsus4", "suspended"), ("Asus4", "suspended"), ("Esus4", "suspended"), ("Bsus4", "suspended"),
                ("Asus2", "suspended"), ("Dsus2", "suspended"), ("Csus2", "suspended"), ("Esus2", "suspended"), ("Gsus2", "suspended"),

                # populaarsemad "add" kitarriakordid
                ("Cadd9", "add"), ("Dadd9", "add"), ("Gadd9", "add"), ("Aadd9", "add"),

                # populaarsemad suurendatud kolmkõlad
                ("Caug", "aug"), ("Daug", "aug"), ("Eaug", "aug"), ("Gaug", "aug"), ("Aaug", "aug"),
            ]
            c.executemany("INSERT INTO chords (chord, category) VALUES (?, ?)", chords)

        connection.commit()



