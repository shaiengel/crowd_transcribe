from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from crowd_transcribe.domain.exceptions import ConflictError, NotFoundError
from crowd_transcribe.domain.schema import (
    Audio,
    AudioList,
    AudioReservation,
    Language,
    MaggidAccent,
    RabbiListItem,
    ReserveAudioRequest,
    TaskDetail,
    TaskEnrichment,
    SubmitTaskRequest,
    SubmitTaskResponse,
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
    rabbi_id: int | None = None,
    svc: AudioService = Depends(_audio_service),
) -> AudioList:
    return svc.list_audios(rabbi_id=rabbi_id)


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


@router.get("/audio/rabbi_list", response_model=list[RabbiListItem])
async def list_rabbis(
    svc: AudioService = Depends(_audio_service),
) -> list[RabbiListItem]:
    return svc.list_rabbis()


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


@router.post("/tasks/start", response_model=AudioReservation, status_code=status.HTTP_201_CREATED)
async def start_task(
    body: ReserveAudioRequest | None = None,
    svc: AudioService = Depends(_audio_service),
    tasks_svc: TasksService = Depends(_tasks_service),
) -> AudioReservation:
    if body is None:
        body = ReserveAudioRequest()
    try:
        if body.media_id:
            reservation = svc.start_audio(media_id=body.media_id)
        else:
            reservation = svc.start_random_audio(accent=body.reading, language=body.language, rabbi_id=body.rabbi_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail="No available audio")
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    try:
        task_detail = tasks_svc.get_task(task_id=reservation.task_id)
        reservation.subtitles = task_detail.subtitles
    except Exception:
        pass
    return reservation


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


@router.put("/tasks/{id}", response_model=SubmitTaskResponse)
async def submit_task(
    id: str,
    body: SubmitTaskRequest,
    svc: TasksService = Depends(_tasks_service),
) -> SubmitTaskResponse:
    try:
        return svc.submit_task(task_id=id, text=body.text)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
