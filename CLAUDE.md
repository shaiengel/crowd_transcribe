# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync                  # Install dependencies
uv run python main.py    # Run entry point
uv run local_test        # Run local Lambda test (once local_test.py exists)
uv build                 # Build wheel for Lambda deployment
```

## Architecture

This project follows the AWS Lambda pattern documented in `python-project-builder.md`. The target structure is:

```
src/crowd_transcribe/
├── __init__.py              # Exports lambda_handler
├── handler.py               # Lambda entry point; initializes DI container
├── config.py                # Dataclass reading from env vars
├── models/schemas.py        # Pydantic models for validation
├── services/                # Business logic, independent of AWS
├── infrastructure/
│   ├── dependency_injection.py  # dependency-injector DI container
│   └── *_client.py          # boto3 wrappers with centralized error handling
└── utils/                   # Shared helpers
```

## Key Patterns

**Three-tier AWS access:** `boto3 client → wrapper class (error handling + logging) → service (business logic)`. Never call boto3 directly from services.

**Dependency injection:** Use `dependency-injector` with `providers.Singleton`. The DI container is constructed once per Lambda invocation in `handler.py`; services receive all dependencies via constructor injection.

**Credential auto-detection:**
```python

    return boto3.Session(profile_name="portal", region_name=region)  # Local: AWS profile
```

**Local testing:** `local_test.py` loads `.env` via `python-dotenv`, constructs a sample event  directly.

**Lambda handler signature:** Always returns `{"statusCode": int, "body": json.dumps(...)}`.
