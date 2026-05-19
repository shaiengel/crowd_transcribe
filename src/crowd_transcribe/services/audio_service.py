import logging
import random
import uuid

from crowd_transcribe.config import Config
from crowd_transcribe.domain.exceptions import NotFoundError
from crowd_transcribe.domain.schema import Audio, AudioList, AudioListItem, AudioReservation, Language, MaggidAccent
from crowd_transcribe.infrastructure.sqlite_db import (
    get_audio_row,
    list_audio_rows,
    list_audio_rows_by_accent,
    pick_and_reserve_audio,
)

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

    def get_random_audio(self, accent: MaggidAccent | None = None, language: Language = Language.HEBREW) -> Audio:
        logger.info("get_random_audio: accent=%s language=%s", accent, language)
        if accent is not None:
            _, rows = list_audio_rows_by_accent(self._db_path, int(accent), int(language))
        else:
            _, rows = list_audio_rows(self._db_path)
        if not rows:
            raise NotFoundError("No available audio")
        r = random.choice(rows)
        return Audio(id=r[0], url=r[1], maggid_description=r[2],
                     massechet_name=r[3], daf_name=r[4], duration=r[5])

    def reserve_random_audio(self, accent: MaggidAccent | None = None, language: Language = Language.HEBREW) -> AudioReservation:
        logger.info("reserve_random_audio: accent=%s language=%s", accent, language)
        task_id = str(uuid.uuid4())
        row = pick_and_reserve_audio(
            self._db_path, task_id,
            accent=int(accent) if accent is not None else None,
            language=int(language),
        )
        if row is None:
            raise NotFoundError("No available audio")
        logger.info("reserve_random_audio: reserved media_id=%s task_id=%s", row[0], task_id)
        return AudioReservation(
            id=row[0], url=row[1], maggid_description=row[2],
            massechet_name=row[3], daf_name=row[4], duration=row[5],
            task_id=task_id,
        )

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
