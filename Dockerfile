FROM python:3.12-slim

ENV UV_PROJECT_ENVIRONMENT=/usr/local

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync --locked --all-extras --no-dev

EXPOSE 8000
CMD [ "uv", "run", "fastapi", "run", "--host", "0.0.0.0", "src/fast_zero/app.py"]
