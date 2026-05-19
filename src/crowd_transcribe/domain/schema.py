from uuid import UUID
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class MaggidAccent(int, Enum):
    ASHKENZY = 1
    SEPHARDI = 2
    CHASSIDIC = 3
    ISRAELI = 4
    OTHER = 5

class Language(int, Enum):
    HEBREW = 1
    ENGLISH = 2
    YIDDISH = 3
    SPANISH = 4
    ARABIC = 5
    FRENCH = 6
    GERMAN = 7
    RUSSIAN = 9   



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


class AudioReservation(Audio):
    task_id: str


class AudioListItem(BaseModel):
    id: str
    maggid_description: Optional[str] = None
    massechet_name: Optional[str] = None
    daf_name: Optional[str] = None
    duration: Optional[int] = None


class AudioList(BaseModel):
    data: list[AudioListItem]
    total: int


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


class ReserveAudioRequest(BaseModel):
    reading: Optional[MaggidAccent] = None
    language: Language = Language.HEBREW


class SubmitTaskRequest(BaseModel):
    text: str


class TaskEnrichment(BaseModel):
    task_id: str
    media_id: str
    text: Optional[str] = None
