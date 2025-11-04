# Dockerfile for FastAPI Transaction Service with Celery and PostgreSQL

# Use official Python base image (slim for smaller size)
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies for PostgreSQL client and build tools
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy poetry.lock and pyproject.toml if using Poetry, else requirements.txt
# Here assuming requirements.txt for simplicity:
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
COPY alembic.ini .
COPY alembic ./alembic

# Expose port the FastAPI app runs on
EXPOSE 8000

# Create a non-root user
RUN adduser --disabled-password --gecos "" appuser

# Change ownership of the app directory
RUN chown -R appuser /app

# Switch to the non-root user
USER appuser

# Command to start the FastAPI app with Uvicorn (adjust module path if needed)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
