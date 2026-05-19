from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from crowd_transcribe.domain.exceptions import NotFoundError
from crowd_transcribe.domain.schema import (
    Audio,
    AudioList,
    AudioReservation,
    Language,
    MaggidAccent,
    ReserveAudioRequest,
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


@router.get("/audios/list", response_model=AudioList)
async def list_audios(
    svc: AudioService = Depends(_audio_service),
) -> AudioList:
    return svc.list_audios()


@router.get("/audios", response_model=Audio)
async def get_random_audio(
    reading: MaggidAccent | None = None,
    language: Language = Language.HEBREW,
    svc: AudioService = Depends(_audio_service),
) -> Audio:
    try:
        return svc.get_random_audio(accent=reading, language=language)
    except NotFoundError:
        return JSONResponse(status_code=200, content={"detail": "Audio not found"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/audios/reserve", response_model=AudioReservation, status_code=status.HTTP_201_CREATED)
async def reserve_audio(
    body: ReserveAudioRequest,
    svc: AudioService = Depends(_audio_service),
) -> AudioReservation:
    try:
        return svc.reserve_random_audio(accent=body.reading, language=body.language)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="No available audio")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


@router.put("/tasks/{id}/submission", status_code=status.HTTP_204_NO_CONTENT)
async def submit_task(
    id: str,
    body: SubmitTaskRequest,
    svc: TasksService = Depends(_tasks_service),
) -> None:
    try:
        svc.submit_task(task_id=id, text=body.text)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
