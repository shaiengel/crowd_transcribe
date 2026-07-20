import logging
import random
import uuid

from crowd_transcribe.config import Config
from crowd_transcribe.domain.exceptions import NotFoundError
from crowd_transcribe.domain.schema import Audio, AudioList, AudioListItem, AudioReservation, Language, MaggidAccent, RabbiListItem
from crowd_transcribe.infrastructure.sqlite_db import (
    get_audio_row,
    get_rabbi_list,
    list_audio_rows,
    list_audio_rows_by_accent,
    list_audio_rows_by_rabbi,
    pick_and_start_audio,
    start_specific_audio,
)

logger = logging.getLogger(__name__)


class AudioService:
    def __init__(self, config: Config) -> None:
        self._db_path = config.sqlite_path
        self._expiration_minutes = config.task_expiration_minutes

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
            _, rows = list_audio_rows_by_accent(self._db_path, int(accent), int(language), self._expiration_minutes)
        else:
            _, all_rows = list_audio_rows(self._db_path, self._expiration_minutes)
            # Filter out in-use items (is_in_use is at index 6)
            rows = [r for r in all_rows if not r[6]]
        if not rows:
            raise NotFoundError("No available audio")
        r = random.choice(rows)
        return Audio(id=r[0], url=r[1], maggid_description=r[2],
                     massechet_name=r[3], daf_name=r[4], duration=r[5])

    def start_random_audio(self, accent: MaggidAccent | None = None, language: Language = Language.HEBREW, rabbi_id: int | None = None) -> AudioReservation:
        logger.info("start_random_audio: accent=%s language=%s rabbi_id=%s", accent, language, rabbi_id)
        task_id = str(uuid.uuid4())
        row = pick_and_start_audio(
            self._db_path, task_id,
            accent=int(accent) if accent is not None else None,
            language=int(language),
            rabbi_id=rabbi_id,
            expiration_minutes=self._expiration_minutes,
        )
        if row is None:
            raise NotFoundError("No available audio")
        logger.info("start_random_audio: started media_id=%s task_id=%s", row[0], task_id)
        return AudioReservation(
            id=row[0], url=row[1], maggid_description=row[2],
            massechet_name=row[3], daf_name=row[4], duration=row[5],
            task_id=task_id,
        )

    def start_audio(self, media_id: str) -> AudioReservation:
        logger.info("start_audio: media_id=%s", media_id)
        task_id = str(uuid.uuid4())
        row = start_specific_audio(
            self._db_path, task_id,
            media_id=media_id,
            expiration_minutes=self._expiration_minutes,
        )
        if row is None:
            raise NotFoundError(f"Media {media_id} not found")
        logger.info("start_audio: started media_id=%s task_id=%s", row[0], task_id)
        return AudioReservation(
            id=row[0], url=row[1], maggid_description=row[2],
            massechet_name=row[3], daf_name=row[4], duration=row[5],
            task_id=task_id,
        )

    def list_rabbis(self) -> list[RabbiListItem]:
        rows = get_rabbi_list(self._db_path)
        return [RabbiListItem(id=r[0], name=r[1]) for r in rows]

    def list_audios(self, rabbi_id: int | None = None) -> AudioList:
        logger.info("list_audios: rabbi_id=%s", rabbi_id)
        if rabbi_id is not None:
            total, rows = list_audio_rows_by_rabbi(self._db_path, rabbi_id)
        else:
            total, rows = list_audio_rows(self._db_path)
        logger.info("list_audios: returning %d/%d records", len(rows), total)
        data = [
            AudioListItem(id=r[0], maggid_description=r[2],
                          massechet_name=r[3], daf_name=r[4], duration=r[5],
                          is_in_use=False)
            for r in rows
        ]
        return AudioList(data=data, total=total)
