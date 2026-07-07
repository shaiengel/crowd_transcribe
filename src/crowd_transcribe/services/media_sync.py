import asyncio
import logging

from crowd_transcribe.config import Config
from crowd_transcribe.domain.file_manager import FileManager
from crowd_transcribe.infrastructure.database import get_connection, get_media_by_id
from crowd_transcribe.infrastructure.sqlite_db import get_existing_ids, init_db, insert_media

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 86_400  # 24 h


class MediaSyncService:
    def __init__(self, file_manager: FileManager, config: Config) -> None:
        self._file_manager = file_manager
        self._config = config
        init_db(config.sqlite_path)

    def _list_s3_ids(self) -> set[str]:
        vtt_keys = self._file_manager.list_keys(self._config.s3_bucket_vtt, suffix=".vtt")
        vtt_ids = {k.split("/")[-1][:-4] for k in vtt_keys}
        mp3_keys = self._file_manager.list_keys(self._config.s3_bucket_mp3, suffix=".mp3")
        mp3_ids = {k.split("/")[-1][:-4] for k in mp3_keys}
        matched = vtt_ids & mp3_ids
        logger.info(
            "media_sync: %d VTTs, %d MP3s, %d matched",
            len(vtt_ids), len(mp3_ids), len(matched),
        )
        return matched

    def sync(self) -> None:
        logger.info(
            "media_sync: listing .vtt from s3://%s and .mp3 from s3://%s",
            self._config.s3_bucket_vtt, self._config.s3_bucket_mp3,
        )
        s3_ids = self._list_s3_ids()
        logger.info("media_sync: found %d files in S3", len(s3_ids))

        existing_ids = get_existing_ids(self._config.sqlite_path)
        new_ids = s3_ids - existing_ids
        non_numeric = {mid for mid in new_ids if not mid.isdigit()}
        if non_numeric:
            logger.info("media_sync: skipping %d non-numeric IDs", len(non_numeric))
            new_ids -= non_numeric
        logger.info("media_sync: %d new IDs to resolve from MSSQL", len(new_ids))

        if not new_ids:
            logger.info("media_sync: nothing to resolve — done")
            return

        resolved = 0
        with get_connection() as conn:
            for media_id in new_ids:
                row = get_media_by_id(conn, media_id)
                if row:
                    insert_media(self._config.sqlite_path, media_id, **row)
                    resolved += 1
                else:
                    logger.warning("media_sync: no record found for media_id=%s", media_id)

        logger.info("media_sync: stored %d new records — done", resolved)

    async def run_forever(self) -> None:
        while True:
            try:
                await asyncio.to_thread(self.sync)
            except Exception:
                logger.exception("media_sync failed")
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
