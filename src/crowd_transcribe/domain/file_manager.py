from abc import ABC, abstractmethod


class FileManager(ABC):
    @abstractmethod
    def list_keys(self, bucket: str, suffix: str = "") -> list[str]:
        """List all keys in a bucket, optionally filtered by suffix."""
        ...
