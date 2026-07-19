
import asyncio
import logging
import uuid

from celery import Celery
from redis import Redis

from showrunner_api.config import get_settings
from showrunner_api.pipeline import run_campaign_pipeline

logger = logging.getLogger(__name__)
settings = get_settings()

celery_app = Celery(
    "showrunner_api",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

try:
    r = Redis.from_url(settings.redis_url, socket_connect_timeout=1)
    r.ping()
    logger.info("Connected to Redis broker.")
except Exception:
    logger.warning("Redis is unreachable. Falling back to Celery task_always_eager mode.")
    celery_app.conf.task_always_eager = True

celery_app.conf.task_default_queue = "showrunner"
celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1

@celery_app.task(name="run_campaign_pipeline", bind=True, max_retries=2)
def run_campaign_pipeline_task(self, project_id: str, workspace_id: str, raw_brief: str) -> None:
    """Celery entrypoint: safely executes the async pipeline in both sync and async runtime contexts."""
    coro = run_campaign_pipeline(
        project_id=uuid.UUID(project_id),
        workspace_id=uuid.UUID(workspace_id),
        raw_brief=raw_brief,
    )
    
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    try:
        if loop and loop.is_running():
            logger.info("Active loop detected. Spawning background task to prevent deadlock...")
            # Schedule it as a background task on the current loop so Uvicorn keeps breathing
            loop.create_task(coro)
        else:
            logger.info("No active event loop found. Starting a fresh loop...")
            asyncio.run(coro)
    except Exception as exc:
        logger.exception("Task failed, attempting retry...")
        raise self.retry(exc=exc, countdown=30) from exc

