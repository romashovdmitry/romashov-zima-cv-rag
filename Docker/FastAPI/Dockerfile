# Use an official lightweight Python image to keep the container small and secure
FROM python:3.11-slim

# Set the application directory inside the container as the current working directory
WORKDIR /app

# Install system-level dependencies required for building Python packages (e.g., PostgreSQL drivers, cryptography)
# --no-install-recommends: Prevents installing unneeded packages to keep the image lean
# rm -rf /var/lib/apt/lists/*: Cleans up the apt cache immediately to reduce layer size
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first to leverage Docker's caching mechanism
# This layer will not re-run unless you modify your requirements.txt
COPY Docker/FastAPI/requirements.txt /app/requirements.txt

# Install Python packages without storing the downloaded wheels/cache inside the container
RUN pip install --no-cache-dir -r requirements.txt

# Copy the core backend source code into the container
COPY app /app

# Set Python path environment variable so Python can properly locate and import internal modules from the root
ENV PYTHONPATH=/app

# Inform Docker that the container listens on port 8000 at runtime (documentation purpose)
EXPOSE 8000

# Execute migrations and start the server using shell execution form
# 1. alembic upgrade head: Automatically runs database migrations before the application starts to prevent schema mismatch
# 2. uvicorn backend.main:app: Starts the high-performance ASGI web server
# --host 0.0.0.0: Mandatory for Docker to bind the app to all network interfaces so it can be reached from the outside
CMD ["sh", "-c", "alembic -c /app/alembic.ini upgrade head && uvicorn backend.main:app --host 0.0.0.0 --port 8000"]