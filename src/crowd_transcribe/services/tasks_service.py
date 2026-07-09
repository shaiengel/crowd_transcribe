import logging
import uuid

from crowd_transcribe.config import Config
from crowd_transcribe.domain.exceptions import ConflictError, NotFoundError
from crowd_transcribe.domain.file_manager import FileManager
from crowd_transcribe.domain.schema import SubmitTaskResponse, TaskDetail, TaskEnrichment, TaskStatus
from crowd_transcribe.utils.text_quality import compute_quality
from crowd_transcribe.infrastructure.sefaria_client import SefariaClient
from crowd_transcribe.infrastructure.sqlite_db import (
    delete_task,
    finish_task,
    get_active_task_for_media,
    get_media_url,
    get_task_enrichment,
    get_task_media_and_quality,
    get_task_media_id,
    get_task_status,
    insert_task,
    task_exists,
)

logger = logging.getLogger(__name__)


class TasksService:
    def __init__(self, config: Config, s3_client: FileManager) -> None:
        self._db_path = config.sqlite_path
        self._bucket = config.s3_bucket_vtt
        self._fixed_bucket = config.s3_fixed_bucket
        self._wer_threshold = config.wer_threshold
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
        insert_task(self._db_path, task_id, media_id, TaskStatus.STARTED)
        logger.info("create_task: created task_id=%s status=%s", task_id, TaskStatus.STARTED)
        return task_id

    def _vtt_bucket(self, quality: str | None) -> str:
        return self._fixed_bucket if quality == "GOOD" else self._bucket

    def get_task(self, task_id: str) -> TaskDetail:
        logger.info("get_task: task_id=%s", task_id)
        row = get_task_media_and_quality(self._db_path, task_id)
        if row is None:
            logger.warning("get_task: task_id=%s not found", task_id)
            raise NotFoundError(f"task {task_id} not found")
        media_id, quality = row
        url = get_media_url(self._db_path, media_id)
        key = f"{media_id}.vtt"
        bucket = self._vtt_bucket(quality)
        vtt = self._s3.get_content(bucket, key)
        logger.info("get_task: task_id=%s quality=%s — VTT served from %s", task_id, quality, bucket)
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
        task_status = get_task_status(self._db_path, task_id)
        if task_status is None:
            logger.warning("delete_task: task_id=%s not found", task_id)
            raise NotFoundError(f"task {task_id} not found")
        if task_status == TaskStatus.FINISHED:
            logger.info("delete_task: task_id=%s is FINISHED, skipping", task_id)
            return
        delete_task(self._db_path, task_id)
        logger.info("delete_task: task_id=%s deleted", task_id)

    def submit_task(self, task_id: str, text: str) -> SubmitTaskResponse:
        logger.info("submit_task: task_id=%s", task_id)
        media_id = get_task_media_id(self._db_path, task_id)
        if media_id is None:
            logger.warning("submit_task: task_id=%s not found", task_id)
            raise NotFoundError(f"task {task_id} not found")
        key = f"{media_id}.vtt"
        wer, wil = None, None
        try:
            reference = self._s3.get_content(self._bucket, key)
            result = compute_quality(reference, text, self._wer_threshold)
            quality, wer, wil = result.quality, result.wer, result.wil
            logger.info("submit_task: task_id=%s WER=%.4f WIL=%.4f quality=%s", task_id, wer, wil, quality)
        except Exception as e:
            logger.warning("submit_task: task_id=%s could not fetch reference VTT for quality check: %s", task_id, e)
            quality = "BAD"
        # Always save with task_id suffix for traceability
        versioned_key = f"{media_id}_{task_id}.vtt"
        self._s3.put_content(self._fixed_bucket, versioned_key, text)
        logger.info("submit_task: task_id=%s saved s3://%s/%s", task_id, self._fixed_bucket, versioned_key)
        # If GOOD, also save as canonical version
        if quality == "GOOD":
            self._s3.put_content(self._fixed_bucket, key, text)
            logger.info("submit_task: task_id=%s saved canonical s3://%s/%s", task_id, self._fixed_bucket, key)
        finish_task(self._db_path, task_id, quality)
        logger.info("submit_task: task_id=%s quality=%s status -> %s", task_id, quality, TaskStatus.FINISHED)
        return SubmitTaskResponse(quality=quality, wer=wer, wil=wil)
