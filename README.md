# Crowd Transcription Fixer — Backend Service

A crowd-sourcing backend where volunteers fix auto-generated subtitles for Talmud audio recordings. Volunteers browse available audios, listen, correct the subtitle text, and submit.

---

## Architecture

```
S3 (original .vtt files)
  │  listed on sync to discover new media IDs
  ▼
MSSQL [dbo].[View_Media]
  │  metadata fetched per ID and stored locally
  ▼
SQLite  (media, tasks, massechet tables)
  │
  ▼
FastAPI  /api/v1/crowd
  ├── GET  /audios            → list unclaimed audios
  ├── GET  /audios/{id}       → audio details
  ├── POST /tasks             → claim audio (creates PENDING task)
  ├── GET  /tasks/{id}        → fetch media URL + VTT → status → STARTED
  ├── GET  /tasks/{id}/enrich → fetch Sefaria Gemara text for the daf
  ├── POST /tasks/{id}/submit → submit corrected text → writes to S3 → FINISHED
  └── DELETE /tasks/{id}      → remove task
```

**Media sync** runs daily and on startup: lists `.vtt` keys in S3, fetches metadata for new IDs from MSSQL, inserts into SQLite.

**Task lifecycle:** `PENDING` (created) → `STARTED` (media fetched) → `FINISHED` (text submitted).

**Enrichment:** `GET /tasks/{id}/enrich` calls the [Sefaria API](https://www.sefaria.org.il) to return the corresponding Gemara text for the daf, which volunteers can use as a reference while correcting.

---

## Project layout

```
src/crowd_transcribe/
├── config.py                    — env var dataclass
├── domain/
│   ├── exceptions.py            — ConflictError, NotFoundError
│   ├── file_manager.py          — FileManager protocol (S3 abstraction)
│   └── schema.py                — Pydantic models
├── infrastructure/
│   ├── database.py              — MSSQL connection via SQLAlchemy + pyodbc
│   ├── dependency_injection.py  — dependency-injector DI container
│   ├── s3_client.py             — boto3 S3 wrapper
│   ├── sefaria_client.py        — Sefaria REST API client
│   └── sqlite_db.py             — SQLite helpers + schema init
└── services/
    ├── audio_service.py         — browse audios from SQLite
    ├── media_sync.py            — S3 → MSSQL → SQLite sync loop
    ├── routes.py                — FastAPI router
    └── tasks_service.py         — task lifecycle and submit logic
openapi.yaml                     — API contract
```

---

## Tech stack

| Layer | Library |
|---|---|
| API framework | FastAPI |
| SQLite | `sqlite3` (stdlib) |
| MSSQL | SQLAlchemy + `pyodbc` |
| AWS S3 | `boto3` |
| Sefaria text | `httpx` |
| DI | `dependency-injector` |
| Package manager | `uv` |

---

## Database schema

```sql
CREATE TABLE media (
    media_id            TEXT PRIMARY KEY,
    url                 TEXT NOT NULL,
    maggid_description  TEXT,
    massechet_id        TEXT,
    massechet_name      TEXT,
    daf_id              TEXT,
    daf_name            TEXT,
    language            TEXT,
    media_duration      INTEGER,
    file_type           TEXT
);

CREATE TABLE tasks (
    task_id         TEXT PRIMARY KEY,
    media_id        TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'PENDING',  -- PENDING | STARTED | FINISHED
    submitted_text  TEXT
);

CREATE TABLE massechet (
    id   TEXT PRIMARY KEY,
    name TEXT NOT NULL
);  -- seeded with tractate name → Sefaria name mapping
```

`list_audios` returns media not yet referenced by any task row.

---

## Environment variables

```env
# AWS
AWS_REGION=us-east-1
AWS_PROFILE=portal
S3_BUCKET=<bucket with original .vtt files>
S3_FIXED_BUCKET=crowd-fixed-subtitles

# MSSQL
DB_HOST=127.0.0.1
DB_PORT=1433
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_DRIVER_WINDOWS=ODBC Driver 17 for SQL Server

# SQLite
SQLITE_PATH=media.db
```

Secrets go in `.env.secret` (loaded after `.env`, takes precedence).

---

## Running locally

```bash
uv sync                  # install dependencies
uv run python main.py    # start the server
uv run local_test        # run local Lambda test (once local_test.py exists)
```

---

## Production server

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

**Base URL:** `https://ai.daf-yomi.com/api/v1/crowd`

**Authentication:** All requests require the `X-API-Key` header with a valid secret key.
