import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

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
