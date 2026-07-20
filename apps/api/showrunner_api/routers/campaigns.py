import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from showrunner_api.auth import AuthenticatedUser, get_current_user
from showrunner_api.infra.db import get_session
from showrunner_api.models import Episode, Project
from showrunner_api.worker import dispatch_campaign_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["campaigns"])


@router.post("/campaigns")
async def create_campaign(
    payload: dict[str, Any],
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """
    Create a new campaign.
    Expects: { raw_brief, title, workspace_id, autostart? }
    Returns: { project_id, status }

    autostart (default true, backward-compatible): if true, the background
    pipeline is dispatched immediately, exactly as before. Pass
    `autostart: false` when the caller needs to upload character-lock
    reference images and/or a brand logo first (see routers/characters.py,
    routers/brand_assets.py) — the pipeline reads locked characters/logo
    at the start of episode 1, so anything uploaded after dispatch races
    the render and may lose. When autostart is false, the returned status
    is "draft"; call POST /api/projects/{project_id}/start once uploads
    are done to kick off the pipeline.

    NOTE: `protagonist_name` / `protagonist_look` / `n_episodes` are no
    longer read here — they were silently dropped by this handler before
    (the model has no columns for them and nothing downstream ever read
    them off this payload). Protagonist identity is now set via the
    character-lock upload endpoint, which is the thing that actually
    reaches storyboard/routing. `n_episodes` still isn't wired into the
    pipeline (run_campaign_pipeline hardcodes its episode count) — that's
    a separate, pre-existing gap in the Writers Room step this endpoint
    can't fix on its own.
    """
    raw_brief = payload.get("raw_brief")
    title = payload.get("title", "Untitled Campaign")
    workspace_id_str = payload.get("workspace_id")
    autostart = payload.get("autostart", True)

    if not raw_brief or not workspace_id_str:
        raise HTTPException(status_code=400, detail="Missing raw_brief or workspace_id")

    try:
        workspace_id = uuid.UUID(workspace_id_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workspace_id format")

    project_id = uuid.uuid4()

    # NOTE: kept for logging only. `Project` (core.py) has no owner_id /
    # user_id column and no FK to `User` at all, so there is currently
    # nowhere in the schema to persist who created a project — this was the
    # source of the previous crash (Project(..., owner_id=...) raised
    # TypeError since that keyword doesn't exist on the model). If per-user
    # ownership needs to be queryable later, that requires an actual
    # migration adding e.g. `created_by: Mapped[uuid.UUID | None] =
    # mapped_column(ForeignKey("users.id"))` to Project first.
    owner_ref = (
        getattr(user, "db_user_id", None)
        or getattr(user, "clerk_id", None)
        or getattr(user, "email", None)
        or "unknown-user"
    )

    # FIXED: Project has no `raw_brief` column — the text field on this
    # model is `concept_prompt` (see core.py), and it's NOT NULL, so it must
    # be populated here rather than left unset.
    project = Project(
        id=project_id,
        workspace_id=workspace_id,
        title=title,
        concept_prompt=raw_brief,
        status="draft" if not autostart else "queued",
    )

    db.add(project)
    await db.commit()

    logger.info("Created project %s for user %s (autostart=%s)", project_id, owner_ref, autostart)

    if not autostart:
        # Caller (dashboard) will upload character locks / logo, then call
        # POST /api/projects/{project_id}/start explicitly.
        return {"project_id": str(project_id), "status": "draft"}

    # FIXED: was `background_tasks.add_task(run_campaign_pipeline_task, ...)`.
    # BackgroundTasks runs sync callables in a worker thread, which forced
    # run_campaign_pipeline_task into asyncio.run() on a *second* new event
    # loop in that thread — separate from the main uvicorn loop the shared
    # DB engine is bound to. Every pipeline run died on its first db.commit()
    # with "attached to a different loop", before any agent (including the
    # LLM call) ever ran. See worker.dispatch_campaign_pipeline for the fix.
    dispatch_campaign_pipeline(
        project_id=str(project_id),
        workspace_id=str(workspace_id),
        raw_brief=raw_brief,
    )

    return {"project_id": str(project_id), "status": "queued"}


@router.post("/projects/{project_id}/start")
async def start_campaign(
    project_id: uuid.UUID,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """
    Dispatches the background pipeline for a project created with
    `autostart: false`. Exists so the dashboard can create the project,
    upload character-lock reference images and/or a brand logo, and only
    then let episode 1 start rendering — closing the race where a shot
    could be generated (and pass the now-real Visual Critic with no
    reference to check against) before the user's upload lands.

    Idempotent against double-clicks: if the project isn't in "draft"
    status, this is a no-op that reports the current status rather than
    dispatching a second pipeline run.
    """
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.status != "draft":
        return {"project_id": str(project_id), "status": project.status, "already_started": True}

    project.status = "queued"
    await db.commit()

    dispatch_campaign_pipeline(
        project_id=str(project_id),
        workspace_id=str(project.workspace_id),
        raw_brief=project.concept_prompt,
    )

    logger.info("Started pipeline for project %s", project_id)
    return {"project_id": str(project_id), "status": "queued", "already_started": False}


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
    result = await db.execute(select(Project).filter(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

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
                # FIXED: Episode has no top-level `synopsis` column — Writers
                # Room stores it inside outline_json (see
                # writers_room.py: outline_json={"synopsis": ...}).
                "synopsis": (ep.outline_json or {}).get("synopsis", "")
                if isinstance(ep.outline_json, dict)
                else "",
                "status": ep.status,
                "assembled_video_url": ep.assembled_video_url,
            }
            for ep in episodes
        ],
    }
