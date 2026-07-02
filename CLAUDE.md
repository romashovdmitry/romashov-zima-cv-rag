## Project Overview

FastAPI-based **RAG (Retrieval-Augmented Generation)** system for replying to HR-managers' questions about candidates. Uses uploaded CVs + candidate form data. Implements **hybrid dense + sparse vector search** with Qdrant, LangGraph, and LangChain.

## Common Commands & Workflow

**Start the full stack:**
```bash
docker-compose -f docker-compose.local.yml up --build
```

**Alembic migrations (run inside the container):**
```bash
docker exec -it fast_api_backend alembic revision --autogenerate -m "description"
docker exec -it fast_api_backend alembic upgrade head
docker exec -it fast_api_backend alembic downgrade -1
```

**Access PostgreSQL directly:**
```bash
docker exec -it postgres psql -U postgres -d rags
```

**Running endpoints:**
- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- Admin panel: `http://localhost:8000/admin`
- Health check: `http://localhost:8000/health`

## Architecture

The app lives under `app/` with `PYTHONPATH=/app`. Entry point is `app/main.py`.

**Module layout:**
- `app/core/` — infrastructure: settings (`config.py`), async SQLAlchemy engine/sessions (`db.py`), FastAPI dependencies (`deps.py`), Qdrant gRPC singleton (`qdrant_engine.py`), sqladmin setup (`admin.py`), startup superuser creation (`initial_data.py`)
- `app/users/` — implemented: ORM models, repository (data access), services (PasswordService, JWTService, UserService), admin views, Pydantic schemas
- `app/cv_uploader/`, `app/retriever/`, `app/indexing/`, `app/generator/` — placeholder directory structure, not yet implemented

**Key design patterns:**
- **Repository pattern** — `UserRepository` is the only DB access point for the users module
- **Service layer** — business logic lives in `*Service` classes, not in endpoints
- **Dependency injection** — JWT auth and `AsyncSession` are injected via `core/deps.py`
- **Soft delete** — `users.deleted_at` timestamp; partial index ensures `email` uniqueness only among alive users
- **Async-first** — all DB operations use `AsyncSession` + `asyncpg`; never use synchronous SQLAlchemy here

**Qdrant:** Uses gRPC (port 6334) rather than HTTP REST for performance. Client is a singleton initialized at startup in `core/qdrant_engine.py`. Hybrid search is planned as dense (BAAI/bge-small-en-v1.5 via fastembed) + sparse (BM25) with Reciprocal Rank Fusion.

**Password hashing:** SHA-256 pre-hash before bcrypt (to handle bcrypt's 72-byte input limit).

**Migrations:** `alembic/versions/` is git-ignored. Always regenerate migrations locally after model changes.

## Configuration

All settings come from `.env` (see `.env.example`). Managed via Pydantic `BaseSettings` in `app/core/config.py`.

Key variable groups: PostgreSQL connection, Qdrant connection, JWT secret/algorithm/expiry, initial superuser credentials, LLM provider (Groq takes priority over Ollama), RAG retrieval parameters, CORS origins.

## Docker Services

`docker-compose.local.yml` runs three services:
- `fast_api_backend` — mounts `./app` for hot-reload; runs `alembic upgrade head` before Uvicorn starts
- `postgres` (PostgreSQL 16-alpine) — db name `rags`
- `vector_db` (Qdrant v1.18) — gRPC on 6334, REST on 6333

## Python & Code Standards

- Follow PEP 8
- Use Google Style docstrings for all public modules, classes, functions and methods
- Prefer composition over inheritance (except where framework requires it)
- Centralize all settings and constants in app/core/config.py
- Extensive type hints
- Structured logging

