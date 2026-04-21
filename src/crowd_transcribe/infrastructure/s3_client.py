import logging

from crowd_transcribe.domain.file_manager import FileManager

logger = logging.getLogger(__name__)


class S3Client(FileManager):
    def __init__(self, client) -> None:
        self._client = client

    def list_keys(self, bucket: str, suffix: str = "") -> list[str]:
        keys = []
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if not suffix or key.endswith(suffix):
                    keys.append(key)
        logger.info(f"Listed {len(keys)} keys in s3://{bucket} (suffix={suffix!r})")
        return keys
