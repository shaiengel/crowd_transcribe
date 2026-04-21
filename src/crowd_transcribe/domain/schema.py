from uuid import UUID
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TaskStatus(str, Enum):
    active = "active"
    submitted = "submitted"
    expired = "expired"
    abandoned = "abandoned"


class Audio(BaseModel):
    id: str
    url: Optional[str] = None
    maggid_description: Optional[str] = None
    massechet_name: Optional[str] = None
    daf_name: Optional[str] = None
    duration: Optional[int] = None


class AudioList(BaseModel):
    data: list[Audio]
    total: int
    offset: int
    limit: int


class Task(BaseModel):
    task_id: UUID
    audio_id: UUID
    status: TaskStatus
    expires_at: int
    seconds_remaining: Optional[int] = None


class TaskCreated(BaseModel):
    task_id: UUID
    session_token: str
    audio: Audio
    expires_at: int
    seconds_remaining: int


class Submission(BaseModel):
    submission_id: UUID
    task_id: UUID
    audio_id: UUID
    fixed_s3_key: str
    submitted_at: int
    byte_size: Optional[int] = None


class CreateTaskRequest(BaseModel):
    audio_id: UUID
