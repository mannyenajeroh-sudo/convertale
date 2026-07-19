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

# FIXED: previously `loop.create_task(coro)` below discarded its return value.
# asyncio only holds a weak reference to a task's owner — if nothing keeps a
# strong reference, the task can be garbage-collected mid-flight, and any
# exception it raises becomes an unretrieved "Task exception was never
# retrieved" warning instead of a real, actionable error (this is literally
# what you saw in the very first crash log in this thread). Keeping tasks in
# this module-level set until they finish prevents that GC race.
_background_tasks: set[asyncio.Task] = set()


def _log_background_result(task: asyncio.Task, *, project_id: str) -> None:
    _background_tasks.discard(task)
    if task.cancelled():
        logger.warning("Pipeline task for project %s was cancelled", project_id)
        return
    exc = task.exception()
    if exc is not None:
        logger.error(
            "❌ Pipeline task for project %s failed in background: %s: %s",
            project_id, type(exc).__name__, exc,
        )
    else:
        logger.info("✓ Pipeline task for project %s finished in background", project_id)


@celery_app.task(name="run_campaign_pipeline", bind=True, max_retries=2)
def run_campaign_pipeline_task(self, project_id: str, workspace_id: str, raw_brief: str) -> None:
    """Celery entrypoint: safely executes the async pipeline in both sync and async runtime contexts.

    NOTE: when an active event loop is already running (i.e. this task is
    invoked in Celery's task_always_eager mode from inside the FastAPI/
    uvicorn process — see the Redis-unreachable fallback above), the pipeline
    is scheduled as a background task rather than run to completion here.
    That means this Celery task reports "success" as soon as scheduling
    succeeds, *not* when the pipeline actually finishes — Celery's
    max_retries/countdown logic below only covers scheduling failures, not
    failures inside the pipeline itself. Those are now at least logged
    clearly (see _log_background_result) instead of silently vanishing, but
    they will NOT trigger a Celery retry. If automatic retries on pipeline
    failure matter, this needs a real Celery worker process with Redis
    available, not the in-process eager fallback.
    """
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
            task = loop.create_task(coro)
            _background_tasks.add(task)
            task.add_done_callback(lambda t: _log_background_result(t, project_id=project_id))
        else:
            logger.info("No active event loop found. Starting a fresh loop...")
            asyncio.run(coro)
    except Exception as exc:
        logger.exception("Task failed, attempting retry...")
        raise self.retry(exc=exc, countdown=30) from exc
