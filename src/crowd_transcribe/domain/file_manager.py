from abc import ABC, abstractmethod


class FileManager(ABC):
    @abstractmethod
    def list_keys(self, bucket: str, suffix: str = "") -> list[str]:
        """List all keys in a bucket, optionally filtered by suffix."""
        ...

    @abstractmethod
    def get_content(self, bucket: str, key: str) -> str:
        """Fetch the text content of an S3 object."""
        ...

    @abstractmethod
    def put_content(self, bucket: str, key: str, content: str) -> None:
        """Upload text content to an S3 object."""
        ...
