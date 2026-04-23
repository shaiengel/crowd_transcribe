import logging

from botocore.exceptions import BotoCoreError, ClientError

from crowd_transcribe.domain.file_manager import FileManager

logger = logging.getLogger(__name__)


class S3Client(FileManager):
    def __init__(self, client) -> None:
        self._client = client

    def list_keys(self, bucket: str, suffix: str = "") -> list[str]:
        try:
            keys = []
            paginator = self._client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=bucket):
                for obj in page.get("Contents", []):
                    key = obj["Key"]
                    if not suffix or key.endswith(suffix):
                        keys.append(key)
            logger.info("Listed %d keys in s3://%s (suffix=%r)", len(keys), bucket, suffix)
            return keys
        except ClientError as e:
            logger.error("list_keys s3://%s failed: %s", bucket, e.response["Error"]["Message"])
            raise
        except BotoCoreError as e:
            logger.error("list_keys s3://%s failed: %s", bucket, e)
            raise

    def get_content(self, bucket: str, key: str) -> str:
        try:
            response = self._client.get_object(Bucket=bucket, Key=key)
            content = response["Body"].read().decode("utf-8")
            logger.info("Fetched s3://%s/%s (%d bytes)", bucket, key, len(content))
            return content
        except ClientError as e:
            code = e.response["Error"]["Code"]
            logger.error("get_content s3://%s/%s failed [%s]: %s", bucket, key, code, e.response["Error"]["Message"])
            raise
        except BotoCoreError as e:
            logger.error("get_content s3://%s/%s failed: %s", bucket, key, e)
            raise

    def put_content(self, bucket: str, key: str, content: str) -> None:
        try:
            self._client.put_object(Bucket=bucket, Key=key, Body=content.encode("utf-8"))
            logger.info("Uploaded s3://%s/%s (%d bytes)", bucket, key, len(content))
        except ClientError as e:
            code = e.response["Error"]["Code"]
            logger.error("put_content s3://%s/%s failed [%s]: %s", bucket, key, code, e.response["Error"]["Message"])
            raise
        except BotoCoreError as e:
            logger.error("put_content s3://%s/%s failed: %s", bucket, key, e)
            raise
