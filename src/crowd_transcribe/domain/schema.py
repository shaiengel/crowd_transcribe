from uuid import UUID
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    STARTED = "STARTED"
    FINISHED = "FINISHED"


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
    task_id: str
    media_id: str
    status: TaskStatus


class TaskCreated(BaseModel):
    task_id: str


class TaskDetail(BaseModel):
    media_link: str
    subtitles: str


class Submission(BaseModel):
    submission_id: UUID
    task_id: UUID
    audio_id: UUID
    fixed_s3_key: str
    submitted_at: int
    byte_size: Optional[int] = None


class CreateTaskRequest(BaseModel):
    media_id: str


class SubmitTaskRequest(BaseModel):
    text: str


class TaskEnrichment(BaseModel):
    task_id: str
    media_id: str
    text: Optional[str] = None
