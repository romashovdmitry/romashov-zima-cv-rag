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

# Swagger doc

```bash
http://localhost:8000/docs
```

# Admin panel

```bash
http://localhost:8000/admin
```

Login with the superuser account configured via env vars.
The superuser is created automatically on the first startup if it does not exist yet.

Add to your `.env`:

```dotenv
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=changeme
```