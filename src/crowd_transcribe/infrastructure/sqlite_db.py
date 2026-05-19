import sqlite3

_MAGGID_DATA_SEED = [
    (15, "הרב דוד קלופפר", 1),
    (16, "הרב אברהם אהרון", 1),
    (17, "הרב אורי בריליאנט", 1),
    (18, "הרב ישראל מינץ", 1),
    (19, "הרב אברהם קרפ", 3),
    (20, "הרב חיים שמרלר", 1),
    (21, "Rabbi Elefant", 2),
    (24, "הרב יהודה אליהו", 1),
    (31, "rabbi yehonatan berger", 2),
    (36, "הרב מתניה ידיד", 1),
    (37, "הרב בנימין מילצקי", 1),
    (38, "Rabbi Simon Wolf", 2),
    (39, "הרב אברהם גרובייס", None),
    (40, "איתמר שטרן", 1),
    (42, "הרב אליהו אורנשטיין", 1),
    (43, "הרב יחזקאל טשינגל", 1),
    (47, "הרב עזרא שרם", 1),
    (49, "rabbi menashe reizman", None),
    (50, "הרב נפתלי וסרמן", 1),
    (51, "", None),
    (54, "הרב משה ביתן", None),
    (55, "", None),
    (64, "", None),
    (67, "", None),
    (69, "הרב אביחי קצין", 1),
    (70, "הרב מנחם בלנק", None),
    (74, "פורטל הדף היומי", None),
    (76, "הרב שמואל נבון", None),
    (78, "", None),
    (82, "רדיו מורשת", None),
    (83, "Rav Daniel Abdelhak", None),
    (84, "", None),
    (85, "", None),
    (86, "", None),
    (87, "", None),
    (88, "", None),
    (89, "", None),
    (91, "", None),
    (92, "", None),
    (93, "", None),
    (94, "הרב אהרן פאהן", None),
    (96, "הרב יהונתן ברגר", None),
    (97, "הרב אייל אונגר", None),
    (98, "הרב פנחס אקרב", None),
    (99, "", None),
    (100, "", None),
    (101, "הרב הראל שפירא", None),
    (102, "Rabbi Rafael Schuster", None),
    (103, "", None),
    (104, "", None),
    (105, "הרב יוסף אלנקווה", None),
    (109, "", None),
    (110, "הרב מאיר שפרכר", 1),
    (113, "", 1),
    (114, "", 1),
    (115, "Rabbi Yechezkel Shamah", None),
    (116, "", None),
    (117, "", None),
    (118, '"חבורת הדף"', None),
    (120, "Shas Illuminated", None),
    (121, "Rabbi Sruly Bornstein", 2),
    (122, "Rav Moshé Franceschi", None),
    (123, "הרב אפרים סגל", None),
    (125, "הרב שמואל דוד פרידמן", None),
    (126, "", None),
    (127, "Rav Yitzchak Lubinshtein", None),
    (128, "הבינני", None),
    (129, '"הדף בעיון"', None),
    (131, "", None),
    (132, "", None),
    (133, "", None),
    (134, "הרב בועז שלום", None),
    (135, "", None),
    (136, "", None),
    (137, "Rabbi Jaim Tuachi", None),
    (138, "Rabbi Shalom Rosner", None),
    (139, "Rabbi Jajam moshe shawat", 4),
    (140, "הרב נחמן ארוש", None),
    (141, "", None),
    (142, "", None),
    (143, "הרב יוני גוטמן", None),
    (144, "", None),
    (145, "", None),
    (146, "Rabbi Chezky Holtzberg", 2),
    (147, "david levchenko, Рав Давид Левченко", 9),
    (148, "Rav Uri Zakhejm", None),
    (149, "Rabino Avigdor Hayut", 4),
    (150, "", None),
    (151, "נתנאל כהן", None),
    (152, "הרב מיכאל קמין", 1),
    (153, "Rabbi Yechezkel Hartman", None),
    (154, "Rav Yossi Amram", 6),
    (155, "הרב מצליח חי מאזוז", 1),
    (156, "", None),
    (157, "", None),
    (158, "", None),
    (159, "", None),
    (160, "הגמרא הדיגיטלית, הרב קובלסקי", 1),
    (161, "הרב מאור דוד כהן", None),
    (162, "הרב ידידיה דהן", 1),
    (163, "הרב יחזקאל הרטמן", None),
    (164, "הרב ישראל כהן", None),
    (165, "", None),
    (166, "", 10),
    (167, "Rabbi Richard Hidary", None),
    (168, "Rav Darren Platzky", None),
    (169, "Rab Ariel Behar", None),
    (170, "Rabi Uri Kelzi", None),
    (171, "הרב הירצקא גרינפעלד", None),
    (172, "הרב דוב מילר", None),
    (173, "", None),
    (174, "Rav Eli Stefansky", 2),
    (175, "הרב גרשון אונגר", None),
    (176, "", None),
    (177, "", None),
    (178, "כאן מורשת, פניני הדף", None),
    (179, "הרב שאול יונתן וינגורט", None),
    (181, "הרב מרדכי רוימי", None),
    (182, "נפתלי רמתי", None),
    (183, "הרב הלל וזאן", None),
    (184, "הרב אלי סטפנסקי", 1),
    (185, "הרב זיסמן", None),
    (186, "הרב אברהם רוט", None),
    (188, "", None),
    (189, "", None),
    (190, "הרב מרקו קצב", 4),
    (191, "Rav Shlomo Grossman", 2),
]

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
                maggid_id           INTEGER,
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS maggid_data (
                id          INTEGER PRIMARY KEY,
                description TEXT,
                language    INTEGER,
                accent      INTEGER
            )
        """)
        conn.executemany(
            "INSERT OR IGNORE INTO massechet (id, name) VALUES (?, ?)",
            _MASSECHET_SEED,
        )
        conn.executemany(
            "INSERT OR IGNORE INTO maggid_data (id, description, language) VALUES (?, ?, ?)",
            _MAGGID_DATA_SEED,
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


def list_audio_rows_by_accent(db_path: str, accent: int = 4, language: int = 1) -> tuple[int, list[tuple]]:
    where = (
        "media.maggid_id = maggid_data.id "
        "AND maggid_data.accent = ? "
        "AND maggid_data.language = ? "
        "AND media.media_id NOT IN (SELECT media_id FROM tasks)"
    )
    params = (accent, language)
    with sqlite3.connect(db_path) as conn:
        total: int = conn.execute(
            f"SELECT COUNT(*) FROM media JOIN maggid_data ON {where}",
            params,
        ).fetchone()[0]
        rows = conn.execute(
            f"""SELECT media.media_id, media.url, media.maggid_description,
                       media.massechet_name, media.daf_name, media.media_duration
                FROM media JOIN maggid_data ON {where}""",
            params,
        ).fetchall()
    return total, rows


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
                 maggid_id: int | None = None,
                 massechet_id: str | None = None,
                 massechet_name: str | None = None,
                 daf_id: str | None = None,
                 daf_name: str | None = None,
                 language: str | None = None,
                 media_duration: int | None = None,
                 file_type: str | None = None) -> None:
    with sqlite3.connect(db_path) as conn:
        if maggid_id is None and maggid_description:
            row = conn.execute(
                "SELECT id FROM maggid_data WHERE LOWER(TRIM(description)) = LOWER(TRIM(?))",
                (maggid_description,),
            ).fetchone()
            if row:
                maggid_id = row[0]
        conn.execute(
            """
            INSERT OR IGNORE INTO media
                (media_id, url, maggid_description, maggid_id, massechet_id, massechet_name,
                 daf_id, daf_name, language, media_duration, file_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (media_id, url, maggid_description, maggid_id, massechet_id, massechet_name,
             daf_id, daf_name, language, media_duration, file_type),
        )
