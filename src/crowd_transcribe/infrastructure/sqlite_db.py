import sqlite3

_MASSECHET_SEED = [
    ("283", "Berakhot"), ("284", "Shabbat"), ("285", "Eruvin"),
    ("286", "Pesachim"), ("287", "Jerusalem_Talmud_Shekalim"), ("288", "Yoma"),
    ("289", "Sukkah"), ("290", "Beitzah"), ("291", "Rosh_Hashanah"),
    ("292", "Taanit"), ("293", "Megillah"), ("294", "Moed_Katan"),
    ("295", "Chagigah"), ("296", "Yevamot"), ("297", "Ketubot"),
    ("298", "Nedarim"), ("299", "Nazir"), ("300", "Sotah"),
    ("301", "Gittin"), ("302", "Kiddushin"), ("303", "Bava_Kamma"),
    ("304", "Bava_Metzia"), ("305", "Bava_Batra"), ("306", "Sanhedrin"),
    ("307", "Makkot"), ("308", "Shevuot"), ("309", "Avodah_Zarah"),
    ("310", "Horayot"), ("311", "Zevachim"), ("312", "Menachot"),
    ("313", "Chullin"), ("314", "Bekhorot"), ("315", "Arakhin"),
    ("316", "Temurah"), ("317", "Keritot"), ("318", "Meilah"),
    ("322", "Niddah"),
]


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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS massechet (
                id   TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        conn.executemany(
            "INSERT OR IGNORE INTO massechet (id, name) VALUES (?, ?)",
            _MASSECHET_SEED,
        )


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


def delete_task(db_path: str, task_id: str) -> bool:
    with sqlite3.connect(db_path) as conn:
        rowcount = conn.execute(
            "DELETE FROM tasks WHERE task_id = ?", (task_id,)
        ).rowcount
    return rowcount > 0


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


def get_audio_row(db_path: str, media_id: str) -> tuple | None:
    with sqlite3.connect(db_path) as conn:
        return conn.execute(
            """SELECT media_id, url, maggid_description, massechet_name,
                      daf_name, media_duration
               FROM media WHERE media_id = ?""",
            (media_id,),
        ).fetchone()


def list_audio_rows(db_path: str) -> tuple[int, list[tuple]]:
    with sqlite3.connect(db_path) as conn:
        total: int = conn.execute(
            "SELECT COUNT(*) FROM media WHERE media_id NOT IN (SELECT media_id FROM tasks)"
        ).fetchone()[0]
        rows = conn.execute(
            """SELECT media_id, url, maggid_description, massechet_name,
                      daf_name, media_duration
               FROM media
               WHERE media_id NOT IN (SELECT media_id FROM tasks)"""
        ).fetchall()
    return total, rows


def get_task_enrichment(db_path: str, task_id: str) -> tuple | None:
    with sqlite3.connect(db_path) as conn:
        return conn.execute(
            """
            SELECT t.media_id, m.massechet_id, ms.name, m.daf_id
            FROM tasks t
            JOIN media m ON m.media_id = t.media_id
            LEFT JOIN massechet ms ON ms.id = m.massechet_id
            WHERE t.task_id = ?
            """,
            (task_id,),
        ).fetchone()


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
