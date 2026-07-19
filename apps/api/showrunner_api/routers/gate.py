import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from showrunner_api.agents.distribution.gate_delivery import GateDeliveryAgent
from showrunner_api.infra.db import get_session
from showrunner_api.models import Project

router = APIRouter(prefix="/api/gate", tags=["gate"])


@router.post("/unlock")
async def unlock_episode(
    payload: dict[str, Any],
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """
    Public endpoint for unlocking a gated episode.
    Requires email, project_id, and episode_id.
    """
    email = payload.get("email")
    project_id = payload.get("project_id")
    episode_id = payload.get("episode_id")

    if not email or not project_id or not episode_id:
        raise HTTPException(status_code=400, detail="email, project_id, and episode_id are required")

    try:
        project_uuid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project_id format")

    # Look up the project's real workspace_id rather than writing a sentinel
    # zero UUID into the AgentJob audit trail (the previous approach) — a
    # public/unauthenticated endpoint doesn't need workspace-scoped auth
    # here, but its job-tracking rows should still point at a real
    # workspace for accurate usage/billing analytics.
    project = (await db.execute(select(Project).where(Project.id == project_uuid))).scalars().first()
    if project is None:
        raise HTTPException(status_code=404, detail="project not found")

    delivery_agent = GateDeliveryAgent(db=db)

    try:
        result = await delivery_agent.execute(
            project_id=project_uuid,
            workspace_id=project.workspace_id,
            episode_id=uuid.UUID(episode_id),
            input_json={
                "project_id": project_id,
                "episode_id": episode_id,
                "email": email,
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result
