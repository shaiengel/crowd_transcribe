import logging
import uuid

from crowd_transcribe.config import Config
from crowd_transcribe.domain.exceptions import ConflictError, NotFoundError
from crowd_transcribe.domain.file_manager import FileManager
from crowd_transcribe.domain.schema import TaskDetail, TaskEnrichment, TaskStatus
from crowd_transcribe.infrastructure.sefaria_client import SefariaClient
from crowd_transcribe.infrastructure.sqlite_db import (
    delete_task,
    finish_task,
    get_active_task_for_media,
    get_media_url,
    get_task_enrichment,
    get_task_media_id,
    insert_task,
    task_exists,
    update_task_status,
)

logger = logging.getLogger(__name__)


class TasksService:
    def __init__(self, config: Config, s3_client: FileManager) -> None:
        self._db_path = config.sqlite_path
        self._bucket = config.s3_bucket
        self._fixed_bucket = config.s3_fixed_bucket
        self._s3 = s3_client
        self._sefaria = SefariaClient()

    def create_task(self, media_id: str) -> str:
        logger.info("create_task: media_id=%s", media_id)
        if get_media_url(self._db_path, media_id) is None:
            logger.warning("create_task: media_id=%s not found", media_id)
            raise NotFoundError(f"media_id {media_id} not found")
        existing = get_active_task_for_media(self._db_path, media_id)
        if existing:
            logger.warning("create_task: media_id=%s already has active task_id=%s", media_id, existing)
            raise ConflictError(f"media_id {media_id} already has an active task")
        while True:
            task_id = str(uuid.uuid4())
            if not task_exists(self._db_path, task_id):
                break
        insert_task(self._db_path, task_id, media_id, TaskStatus.PENDING)
        logger.info("create_task: created task_id=%s status=%s", task_id, TaskStatus.PENDING)
        return task_id

    def get_task(self, task_id: str) -> TaskDetail:
        logger.info("get_task: task_id=%s", task_id)
        media_id = get_task_media_id(self._db_path, task_id)
        if media_id is None:
            logger.warning("get_task: task_id=%s not found", task_id)
            raise NotFoundError(f"task {task_id} not found")
        logger.info("get_task: task_id=%s media_id=%s — fetching url and VTT", task_id, media_id)
        url = get_media_url(self._db_path, media_id)
        vtt = self._s3.get_content(self._bucket, f"{media_id}.vtt")
        update_task_status(self._db_path, task_id, TaskStatus.STARTED)
        logger.info("get_task: task_id=%s status -> %s", task_id, TaskStatus.STARTED)
        return TaskDetail(media_link=url, subtitles=vtt)

    def enrich_task(self, task_id: str) -> TaskEnrichment:
        logger.info("enrich_task: task_id=%s", task_id)
        row = get_task_enrichment(self._db_path, task_id)
        if row is None:
            logger.warning("enrich_task: task_id=%s not found", task_id)
            raise NotFoundError(f"task {task_id} not found")
        media_id, _massechet_id, massechet_name, daf_id = row
        text = None
        if massechet_name and daf_id:
            try:
                text = self._sefaria.fetch_daf(massechet_name, int(daf_id))
            except Exception as e:
                logger.warning("enrich_task: Sefaria fetch failed for task_id=%s: %s", task_id, e)
        return TaskEnrichment(task_id=task_id, media_id=media_id, text=text)

    def delete_task(self, task_id: str) -> None:
        logger.info("delete_task: task_id=%s", task_id)
        if not delete_task(self._db_path, task_id):
            logger.warning("delete_task: task_id=%s not found", task_id)
            raise NotFoundError(f"task {task_id} not found")
        logger.info("delete_task: task_id=%s deleted", task_id)

    def submit_task(self, task_id: str, text: str) -> None:
        logger.info("submit_task: task_id=%s", task_id)
        media_id = get_task_media_id(self._db_path, task_id)
        if media_id is None:
            logger.warning("submit_task: task_id=%s not found", task_id)
            raise NotFoundError(f"task {task_id} not found")
        key = f"{media_id}.vtt"
        self._s3.put_content(self._fixed_bucket, key, text)
        finish_task(self._db_path, task_id, text)
        logger.info("submit_task: task_id=%s saved s3://%s/%s status -> %s", task_id, self._fixed_bucket, key, TaskStatus.FINISHED)
