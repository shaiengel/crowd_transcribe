import logging

from crowd_transcribe.config import Config
from crowd_transcribe.domain.schema import Audio, AudioList, AudioListItem
from crowd_transcribe.infrastructure.sqlite_db import get_audio_row, list_audio_rows

logger = logging.getLogger(__name__)


class AudioService:
    def __init__(self, config: Config) -> None:
        self._db_path = config.sqlite_path

    def get_audio(self, media_id: str) -> Audio | None:
        logger.info("get_audio: media_id=%s", media_id)
        row = get_audio_row(self._db_path, media_id)
        if row is None:
            logger.warning("get_audio: media_id=%s not found", media_id)
            return None
        return Audio(id=row[0], url=row[1], maggid_description=row[2],
                     massechet_name=row[3], daf_name=row[4], duration=row[5])

    def list_audios(self) -> AudioList:
        logger.info("list_audios")
        total, rows = list_audio_rows(self._db_path)
        logger.info("list_audios: returning %d/%d records", len(rows), total)
        data = [
            AudioListItem(id=r[0], maggid_description=r[2],
                          massechet_name=r[3], daf_name=r[4], duration=r[5])
            for r in rows
        ]
        return AudioList(data=data, total=total)
