# romashov-zima-cv-rag
RAG-system to reply hrs

## Route To check FastAPI health

```bash
http://localhost:8000/health
```

## Alembic commands

To update alembic migrations

```bash
docker exec -it fast_api_backend alembic revision --autogenerate -m "YOUR COMMENT"
```

To apply alembic migrations

```bash
docker exec -it fast_api_backend alembic upgrade head
```

# To enter in postgres (locally)

```bash
docker exec -it postgres psql -U postgres -d rags
```