import asyncio
import logging
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from pathlib import Path

from fastapi import FastAPI

_fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=_fmt)

Path("log").mkdir(exist_ok=True)
_file_handler = RotatingFileHandler("log/app.log", maxBytes=10_000_000, backupCount=3, encoding="utf-8")
_file_handler.setFormatter(logging.Formatter(_fmt))
logging.getLogger().addHandler(_file_handler)

from crowd_transcribe.infrastructure.dependency_injection import DependenciesContainer
from crowd_transcribe.services.routes import router


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    for route in app.routes:
        if hasattr(route, "methods"):
            logger.info("  %-30s %s", route.path, ", ".join(sorted(route.methods)))

    container = DependenciesContainer()
    app.state.container = container
    task = asyncio.create_task(container.media_sync().run_forever())
    yield
    task.cancel()


app = FastAPI(title="Crowd Transcription Fixer API", version="1.0.0", lifespan=lifespan)
app.include_router(router)
