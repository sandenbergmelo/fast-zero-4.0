#!/usr/bin/env sh

# Execute the migrations
uv run alembic upgrade head

# Start the FastAPI application
uv run fastapi run --host 0.0.0.0 --port 8000 src/fast_zero/app.py
