# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync                  # Install dependencies
uv run python main.py    # Run the FastAPI server
uv build                 # Build wheel
```

## Architecture

FastAPI service (`main.py`) with a `dependency-injector` DI container initialized in the lifespan hook. A background task runs `MediaSyncService.run_forever()` (daily sync loop).

```
src/crowd_transcribe/
├── config.py                    # Dataclass reading from env vars (.env + .env.secret)
├── domain/
│   ├── exceptions.py            # ConflictError, NotFoundError
│   ├── file_manager.py          # FileManager protocol (S3 abstraction)
│   └── schema.py                # Pydantic models (Audio, Task, TaskDetail, TaskEnrichment, …)
├── infrastructure/
│   ├── database.py              # MSSQL connection via SQLAlchemy + pyodbc
│   ├── dependency_injection.py  # DependenciesContainer (providers.Singleton)
│   ├── s3_client.py             # boto3 S3 wrapper (implements FileManager)
│   ├── sefaria_client.py        # Sefaria REST API client (fetches Gemara text)
│   └── sqlite_db.py             # SQLite helpers + schema init (init_db called on startup)
└── services/
    ├── audio_service.py         # list_audios / get_audio — reads SQLite media table
    ├── media_sync.py            # S3 → MSSQL → SQLite sync; runs every 24 h
    ├── routes.py                # FastAPI router (prefix /api/v1)
    └── tasks_service.py         # Task lifecycle: create, get, enrich, delete, submit
```

## Key Patterns

**Three-tier data access:** `boto3/pyodbc → infrastructure wrapper → service`. Never call boto3 or SQLAlchemy directly from services.

**Dependency injection:** `dependency-injector` with `providers.Singleton`. The container is created once in the FastAPI lifespan and stored on `app.state.container`. Routes resolve services via `request.app.state.container.<service>()`.

**AWS credentials:** `boto3.Session(profile_name=config.aws_profile, region_name=config.aws_region)` — uses the `portal` AWS profile locally.

**SQLite schema:** Initialized by `init_db()` on startup (called from `MediaSyncService.__init__`). Tables: `media`, `tasks`, `massechet` (tractate seed data).

**Task status flow:** `PENDING` (created) → `STARTED` (GET /tasks/{id} fetches media + VTT) → `FINISHED` (POST /tasks/{id}/submit writes fixed VTT to S3).

**Media sync:** `MediaSyncService` lists `.vtt` keys in S3, finds IDs not yet in SQLite, fetches metadata from MSSQL `[dbo].[View_Media]`, and inserts rows. Runs daily and once at startup.

**Sefaria enrichment:** `GET /tasks/{id}/enrich` looks up `massechet_name` + `daf_id` from SQLite, fetches both amudim (A/B) from the Sefaria v3 API, strips nikud and HTML, and returns the concatenated text. Failures are logged and return `text: null`.

**API contract:** `openapi.yaml` is the source of truth for endpoint shapes.
