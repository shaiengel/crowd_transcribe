from dataclasses import dataclass
from uuid import UUID
from enum import Enum
from typing import Optional

from pydantic import BaseModel


@dataclass
class QualityResult:
    quality: str
    wer: float
    wil: float


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
    subtitles: Optional[str] = None


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
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    quality: Optional[str] = None


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


class SubmitTaskResponse(BaseModel):
    quality: str
    wer: Optional[float] = None
    wil: Optional[float] = None


class TaskEnrichment(BaseModel):
    task_id: str
    media_id: str
    text: Optional[str] = None
