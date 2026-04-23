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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id         TEXT PRIMARY KEY,
                media_id        TEXT NOT NULL,
                status          TEXT NOT NULL DEFAULT 'PENDING',
                submitted_text  TEXT
            )
        """)


def insert_task(db_path: str, task_id: str, media_id: str, status: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO tasks (task_id, media_id, status) VALUES (?, ?, ?)",
            (task_id, media_id, status),
        )


def task_exists(db_path: str, task_id: str) -> bool:
    with sqlite3.connect(db_path) as conn:
        return conn.execute(
            "SELECT 1 FROM tasks WHERE task_id = ?", (task_id,)
        ).fetchone() is not None


def get_task_media_id(db_path: str, task_id: str) -> str | None:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT media_id FROM tasks WHERE task_id = ?", (task_id,)
        ).fetchone()
    return row[0] if row else None


def update_task_status(db_path: str, task_id: str, status: str) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "UPDATE tasks SET status = ? WHERE task_id = ?", (status, task_id)
        )


def get_media_url(db_path: str, media_id: str) -> str | None:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT url FROM media WHERE media_id = ?", (media_id,)
        ).fetchone()
    return row[0] if row else None


def get_active_task_for_media(db_path: str, media_id: str) -> str | None:
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT task_id FROM tasks WHERE media_id = ? AND status IN ('PENDING', 'STARTED')",
            (media_id,),
        ).fetchone()
    return row[0] if row else None


def finish_task(db_path: str, task_id: str, text: str) -> bool:
    with sqlite3.connect(db_path) as conn:
        rowcount = conn.execute(
            "UPDATE tasks SET status = 'FINISHED', submitted_text = ? WHERE task_id = ?",
            (text, task_id),
        ).rowcount
    return rowcount > 0


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
