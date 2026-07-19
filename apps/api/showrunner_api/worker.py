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

# Detect if Redis is running; if not, fallback to Celery eager mode to allow
# in-process synchronous execution for local development without Redis.
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
    """Celery entrypoint: runs the async campaign pipeline to completion.

    NOTE: previously this module only instantiated the Celery ``app`` object
    with zero ``@celery_app.task`` definitions. The Helm chart
    (worker-deployment.yaml) deploys a whole fleet of pods running
    `celery -A showrunner_api.worker worker`, but with no tasks registered
    they would boot and sit idle forever — meanwhile the real pipeline ran
    in-process on the API server via FastAPI BackgroundTasks (in-memory,
    lost on restart, not retried, not distributed). This task is what
    `routers/campaigns.py` now actually dispatches to.

    Celery workers execute tasks synchronously by default, so the async
    pipeline is driven with ``asyncio.run`` inside the task body. Each
    worker process handles one task at a time (see ``task_acks_late`` /
    ``worker_prefetch_multiplier`` above), which keeps this safe for the
    pipeline's async DB/HTTP clients.
    """
    try:
        asyncio.run(
            run_campaign_pipeline(
                project_id=uuid.UUID(project_id),
                workspace_id=uuid.UUID(workspace_id),
                raw_brief=raw_brief,
            )
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30) from exc
