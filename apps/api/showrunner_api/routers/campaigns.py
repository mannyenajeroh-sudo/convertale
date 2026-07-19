import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from showrunner_api.auth import AuthenticatedUser, get_current_user
from showrunner_api.infra.db import get_session
from showrunner_api.models import Project, Episode
from showrunner_api.worker import run_campaign_pipeline_task

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["campaigns"])

@router.post("/campaigns")
async def create_campaign(
    payload: dict[str, Any],
    background_tasks: BackgroundTasks,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """
    Create a new campaign and start the background pipeline.
    Expects: { raw_brief, title, workspace_id, protagonist_name, protagonist_look, n_episodes }
    Returns: { project_id, status: "queued" }
    """
    raw_brief = payload.get("raw_brief")
    title = payload.get("title", "Untitled Campaign")
    workspace_id_str = payload.get("workspace_id")
    
    if not raw_brief or not workspace_id_str:
        raise HTTPException(status_code=400, detail="Missing raw_brief or workspace_id")

    try:
        workspace_id = uuid.UUID(workspace_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workspace_id format")

    # Create Project record
    project_id = uuid.uuid4()
    
    # FIX: Check what attribute your AuthenticatedUser actually has
    # Common names: 'sub', 'user_id', 'id'
    owner_id = getattr(user, 'user_id', None) or getattr(user, 'sub', None) or str(user)
    
    project = Project(
        id=project_id,
        workspace_id=workspace_id,
        owner_id=owner_id,
        title=title,
        status="queued",
        raw_brief=raw_brief,
    )
    
    db.add(project)
    await db.commit()
    
    logger.info("Created project %s for user %s", project_id, owner_id)

    # Start the background pipeline
    background_tasks.add_task(
        run_campaign_pipeline_task,
        project_id=str(project_id),
        workspace_id=str(workspace_id),
        raw_brief=raw_brief
    )

    return {"project_id": str(project_id), "status": "queued"}

@router.get("/projects/{project_id}/episodes")
async def get_episodes(
    project_id: uuid.UUID,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """
    Retrieves all episodes for a specific project.
    Used by the frontend dashboard to poll for progress.
    """
    # Verify the project exists
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Fetch episodes linked to this project
    result = await db.execute(
        select(Episode)
        .filter(Episode.project_id == project_id)
        .order_by(Episode.episode_number.asc())
    )
    episodes = result.scalars().all()

    return {
        "episode_count": len(episodes),
        "episodes": [
            {
                "episode_id": str(ep.id),
                "episode_number": ep.episode_number,
                "title": ep.title,
                "synopsis": ep.synopsis,
                "status": ep.status,
                "assembled_video_url": ep.assembled_video_url,
                "identity_score": getattr(ep, 'identity_score', None),
            } 
            for ep in episodes
        ]
    }