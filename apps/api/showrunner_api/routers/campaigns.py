import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from showrunner_api.auth import AuthenticatedUser, get_current_user
from showrunner_api.infra.db import get_session
from showrunner_api.models import Project
from showrunner_api.worker import run_campaign_pipeline_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.post("")
async def create_campaign(
    payload: dict[str, Any],
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Creates a new campaign project and enqueues the pipeline on the Celery worker fleet."""
    workspace_id_str = payload.get("workspace_id")
    raw_brief = payload.get("raw_brief")

    if not workspace_id_str or not raw_brief:
        raise HTTPException(status_code=400, detail="workspace_id and raw_brief are required")

    try:
        workspace_id = uuid.UUID(workspace_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workspace_id format")

    project = Project(
        workspace_id=workspace_id,
        title=payload.get("title", "New Campaign"),
        concept_prompt=raw_brief,
        status="generating_arc",
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    # Dispatch to the Celery worker fleet instead of running in-process.
    # NOTE: previously this used FastAPI's BackgroundTasks, which runs the
    # entire multi-agent pipeline inside the API server's own process —
    # not distributed, not durable across restarts, and not retried on
    # failure, despite a dedicated Celery + Redis worker fleet already being
    # provisioned for exactly this (infra/helm/showrunner).
    run_campaign_pipeline_task.delay(str(project.id), str(workspace_id), raw_brief)

    return {
        "project_id": str(project.id),
        "status": project.status,
        "message": "Pipeline queued for background processing.",
    }
