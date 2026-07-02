from collections.abc import Generator

from qdrant_client import QdrantClient

from core.config import settings

# Singleton client. gRPC (port 6334) is significantly faster than HTTP REST.
qdrant_client = QdrantClient(
    host=settings.qdrant_host,
    grpc_port=settings.qdrant_port,
    prefer_grpc=True,
    api_key=settings.qdrant_api_key or None,
)


def get_qdrant() -> Generator[QdrantClient, None, None]:
    """FastAPI dependency — yields the shared Qdrant client."""
    yield qdrant_client