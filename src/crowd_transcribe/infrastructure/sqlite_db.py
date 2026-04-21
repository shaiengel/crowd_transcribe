import sqlite3


def init_db(db_path: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS media (
                media_id            TEXT PRIMARY KEY,
                url                 TEXT NOT NULL,
                maggid_description  TEXT,
                massechet_id        TEXT,
                massechet_name      TEXT,
                daf_id              TEXT,
                daf_name            TEXT,
                language            TEXT,
                media_duration      INTEGER,
                file_type           TEXT
            )
        """)


def get_existing_ids(db_path: str) -> set[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT media_id FROM media").fetchall()
    return {row[0] for row in rows}


def insert_media(db_path: str, media_id: str, url: str,
                 maggid_description: str | None = None,
                 massechet_id: str | None = None,
                 massechet_name: str | None = None,
                 daf_id: str | None = None,
                 daf_name: str | None = None,
                 language: str | None = None,
                 media_duration: int | None = None,
                 file_type: str | None = None) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO media
                (media_id, url, maggid_description, massechet_id, massechet_name,
                 daf_id, daf_name, language, media_duration, file_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (media_id, url, maggid_description, massechet_id, massechet_name,
             daf_id, daf_name, language, media_duration, file_type),
        )
