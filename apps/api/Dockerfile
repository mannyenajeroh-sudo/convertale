FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.5

WORKDIR /app

# ffmpeg is required at runtime by AssemblyAgent (clip concatenation +
# subtitle burn-in) and VisualCriticAgent (frame extraction via ffprobe).
# It was previously never installed, so both agents would fail with
# FileNotFoundError as soon as they tried to shell out to `ffmpeg`/`ffprobe`.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root --no-interaction --no-ansi

COPY showrunner_api ./showrunner_api

RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /tmp/convertale_jobs \
    && chown -R appuser:appuser /app /tmp/convertale_jobs
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "showrunner_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
