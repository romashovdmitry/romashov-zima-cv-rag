"""FastAPI application entry point with startup lifespan."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.admin import create_admin
from core.config import settings
from core.initial_data import create_superuser_if_missing

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Liveness probe response"""

    status: str


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await create_superuser_if_missing()
    yield


app = FastAPI(
    title="My Personal CV RAG System",
    description=(
        "RAG system for matching candidates to IT vacancies using hybrid "
        "dense+sparse search (Qdrant) and LangGraph orchestration."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

create_admin(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(any_router, prefix="/api/v1")


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Check API liveness",
    description="Returns a simple status payload when the backend process is alive.",
)
async def health() -> HealthResponse:
    """Liveness probe endpoint."""
    return HealthResponse(status="ok")
