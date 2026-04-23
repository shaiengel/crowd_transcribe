from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from crowd_transcribe.domain.exceptions import ConflictError, NotFoundError
from crowd_transcribe.domain.schema import (
    Audio,
    AudioList,
    CreateTaskRequest,
    TaskCreated,
    TaskDetail,
    TaskEnrichment,
    SubmitTaskRequest,
)
from crowd_transcribe.services.audio_service import AudioService
from crowd_transcribe.services.tasks_service import TasksService

router = APIRouter(prefix="/api/v1/crowd")


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

def _tasks_service(request: Request) -> TasksService:
    return request.app.state.container.tasks_service()


@router.post("/tasks", response_model=TaskCreated, status_code=status.HTTP_201_CREATED)
async def create_task(
    body: CreateTaskRequest,
    svc: TasksService = Depends(_tasks_service),
) -> TaskCreated:
    try:
        task_id = svc.create_task(media_id=body.media_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return TaskCreated(task_id=task_id)


@router.get("/tasks/{id}", response_model=TaskDetail)
async def get_task(
    id: str,
    svc: TasksService = Depends(_tasks_service),
) -> TaskDetail:
    try:
        return svc.get_task(task_id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/tasks/{id}/enrich", response_model=TaskEnrichment)
async def enrich_task(
    id: str,
    svc: TasksService = Depends(_tasks_service),
) -> TaskEnrichment:
    try:
        return svc.enrich_task(task_id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    id: str,
    svc: TasksService = Depends(_tasks_service),
) -> None:
    try:
        svc.delete_task(task_id=id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/tasks/{id}/submit", status_code=status.HTTP_204_NO_CONTENT)
async def submit_task(
    id: str,
    body: SubmitTaskRequest,
    svc: TasksService = Depends(_tasks_service),
) -> None:
    try:
        svc.submit_task(task_id=id, text=body.text)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
