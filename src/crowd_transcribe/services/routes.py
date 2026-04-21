from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from crowd_transcribe.domain.schema import (
    Audio,
    AudioList,
    CreateTaskRequest,
    Submission,
    Task,
    TaskCreated,
)
from crowd_transcribe.services.audio_service import AudioService

router = APIRouter(prefix="/api/v1")
session_bearer = HTTPBearer()


# ---------------------------------------------------------------------------
# Audios
# ---------------------------------------------------------------------------

def _audio_service(request: Request) -> AudioService:
    return request.app.state.container.audio_service()


@router.get("/audios", response_model=AudioList)
async def list_audios(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    svc: AudioService = Depends(_audio_service),
) -> AudioList:
    return svc.list_audios(limit=limit, offset=offset)


@router.get("/audios/{id}", response_model=Audio)
async def get_audio(id: str, svc: AudioService = Depends(_audio_service)) -> Audio:
    audio = svc.get_audio(id)
    if audio is None:
        raise HTTPException(status_code=404, detail="Audio not found")
    return audio


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

@router.post("/tasks", response_model=TaskCreated, status_code=status.HTTP_201_CREATED)
async def create_task(body: CreateTaskRequest) -> TaskCreated:
    raise NotImplementedError


@router.get("/tasks/{id}", response_model=Task)
async def get_task(
    id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(session_bearer),
) -> Task:
    raise NotImplementedError


@router.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def abandon_task(
    id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(session_bearer),
) -> None:
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Subtitles
# ---------------------------------------------------------------------------

@router.get("/tasks/{id}/subtitles")
async def get_subtitles(
    id: UUID,
    credentials: HTTPAuthorizationCredentials = Depends(session_bearer),
) -> Response:
    raise NotImplementedError


@router.post("/tasks/{id}/subtitles", response_model=Submission)
async def submit_subtitles(
    id: UUID,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(session_bearer),
) -> Submission:
    raise NotImplementedError
