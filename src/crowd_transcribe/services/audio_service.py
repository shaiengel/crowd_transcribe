import sqlite3

from crowd_transcribe.config import Config
from crowd_transcribe.domain.schema import Audio, AudioList


class AudioService:
    def __init__(self, config: Config) -> None:
        self._db_path = config.sqlite_path

    def get_audio(self, media_id: str) -> Audio | None:
        with sqlite3.connect(self._db_path) as conn:
            row = conn.execute(
                """SELECT media_id, url, maggid_description, massechet_name,
                          daf_name, media_duration
                   FROM media WHERE media_id = ?""",
                (media_id,),
            ).fetchone()
        if row is None:
            return None
        return Audio(id=row[0], url=row[1], maggid_description=row[2],
                     massechet_name=row[3], daf_name=row[4], duration=row[5])

    def list_audios(self, limit: int, offset: int) -> AudioList:
        with sqlite3.connect(self._db_path) as conn:
            total: int = conn.execute("SELECT COUNT(*) FROM media").fetchone()[0]

            rows = conn.execute(
                """SELECT media_id, url, maggid_description, massechet_name,
                          daf_name, media_duration
                   FROM media
                   LIMIT ? OFFSET ?""",
                (limit, offset),
            ).fetchall()

        data = [
            Audio(id=r[0], url=r[1], maggid_description=r[2],
                  massechet_name=r[3], daf_name=r[4], duration=r[5])
            for r in rows
        ]
        return AudioList(data=data, total=total, offset=offset, limit=limit)
