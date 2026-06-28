from typing import Generator
from qdrant_client import QdrantClient
from core.config import settings

# Инициализируем синглтон клиента. 
# Используем gRPC (порт 6334) — он в разы быстрее, чем HTTP REST API.
qdrant_client = QdrantClient(
    host=settings.QDRANT_HOST,
    grpc_port=settings.QDRANT_PORT,
    prefer_grpc=True,
    api_key=settings.QDRANT_API_KEY
)

# Зависимость (Dependency) для эндпоинтов
def get_qdrant() -> Generator[QdrantClient, None, None]:
    # Клиент Qdrant сам управляет пулом соединений, 
    # поэтому просто отдаем его в контекст запроса
    yield qdrant_client