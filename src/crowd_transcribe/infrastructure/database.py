import os
from contextlib import contextmanager
from typing import Generator
from urllib.parse import quote_plus

from sqlalchemy import Connection, create_engine
from sqlalchemy.engine import Engine

_engine: Engine | None = None


def _get_connection_string() -> str:
    driver   = os.getenv("DB_DRIVER_WINDOWS", "ODBC Driver 17 for SQL Server")
    host     = os.getenv("DB_HOST", "127.0.0.1")
    port     = os.getenv("DB_PORT", "1433")
    database = os.getenv("DB_NAME", "")
    user     = os.getenv("DB_USER", "")
    password = quote_plus(os.getenv("DB_PASSWORD", ""))
    driver   = quote_plus(driver)
    return f"mssql+pyodbc://{user}:{password}@{host}:{port}/{database}?driver={driver}"


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(_get_connection_string())
    return _engine


@contextmanager
def get_connection() -> Generator[Connection, None, None]:
    with get_engine().connect() as conn:
        yield conn


def get_media_by_id(conn: Connection, media_id: str) -> dict | None:
    from sqlalchemy import text
    result = conn.execute(
        text("""
            SELECT media_link, maggid_description, massechet_id, massechet_name,
                   daf_id, daf_name, language_en, media_duration, file_type
            FROM [dbo].[View_Media]
            WHERE media_id = :id AND media_is_active = 1
        """),
        {"id": media_id},
    ).fetchone()
    if result is None:
        return None
    return {
        "url":                 result.media_link,
        "maggid_description":  result.maggid_description,
        "massechet_id":        result.massechet_id,
        "massechet_name":      result.massechet_name,
        "daf_id":              result.daf_id,
        "daf_name":            result.daf_name,
        "language":            result.language_en,
        "media_duration":      result.media_duration,
        "file_type":           result.file_type,
    }
