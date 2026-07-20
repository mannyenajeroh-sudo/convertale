import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from showrunner_api.auth import AuthenticatedUser, get_current_user
from showrunner_api.infra.db import get_session
from showrunner_api.models import Project
from showrunner_api.worker import run_campaign_pipeline_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.post("")
async def create_campaign(
    raw_brief: str = Form(...),
    title: str = Form(...),
    workspace_id: str = Form(...),
    protagonist_name: str | None = Form(None),
    protagonist_look: str | None = Form(None),
    n_episodes: int = Form(2),
    character_image: UploadFile | None = None,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Creates a new campaign project and enqueues the pipeline on the Celery worker fleet.
    
    Accepts optional character image upload for locked appearance reference.
    """
    try:
        workspace_id_uuid = uuid.UUID(workspace_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workspace_id format")

    # Handle character image upload if provided
    character_image_url = None
    if character_image and character_image.filename:
        # Store uploaded image - in production this would go to S3/GCS
        # For now, we'll store a placeholder path that can be enhanced later
        file_extension = character_image.filename.split(".")[-1] if "." in character_image.filename else "png"
        character_image_url = f"/uploads/characters/{uuid.uuid4()}.{file_extension}"
        # Read and store the file content (in production, upload to cloud storage)
        image_content = await character_image.read()
        logger.info(f"Character image uploaded: {character_image.filename}, size: {len(image_content)} bytes")
        # TODO: Implement actual file storage (S3, GCS, or local filesystem)
        # For now, just log the upload - the URL is stored for future use

    project = Project(
        workspace_id=workspace_id_uuid,
        title=title,
        concept_prompt=raw_brief,
        status="generating_arc",
        protagonist_name=protagonist_name,
        protagonist_look=protagonist_look,
        protagonist_image_url=character_image_url,
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
        "character_image_url": character_image_url,
        "message": "Pipeline queued for background processing.",
    }
