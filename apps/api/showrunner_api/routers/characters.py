import logging
import uuid
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from showrunner_api.agents.production.assembly import BACKEND_BASE_URL, MEDIA_DIR
from showrunner_api.auth import AuthenticatedUser, get_current_user
from showrunner_api.infra.db import get_session
from showrunner_api.models import Project
from showrunner_api.services.series_bible import SeriesBibleService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["characters"])

_ALLOWED_SLOTS = {"primary", "secondary"}
_ALLOWED_CONTENT_TYPES = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
_MAX_UPLOAD_BYTES = 8 * 1024 * 1024  # 8MB — a reference still doesn't need to be larger than this


def _ref_image_url(ref_image_path: str | None) -> str | None:
    """MEDIA_DIR is mounted at /media (see main.py); character refs are
    saved under MEDIA_DIR/characters/..., so they're already web-servable —
    this just turns the on-disk path into the URL the dashboard can put in
    an <img src>."""
    if not ref_image_path:
        return None
    try:
        rel = Path(ref_image_path).resolve().relative_to(MEDIA_DIR)
    except ValueError:
        return None
    return f"{BACKEND_BASE_URL}/media/{rel.as_posix()}"


async def _get_project_or_404(project_id: uuid.UUID, db: AsyncSession) -> Project:
    project = (await db.execute(select(Project).where(Project.id == project_id))).scalars().first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/{project_id}/characters")
async def list_characters(
    project_id: uuid.UUID,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Current lock state for both character slots, for the dashboard to render."""
    await _get_project_or_404(project_id, db)
    service = SeriesBibleService(db=db)
    chars = await service.list_characters(project_id)

    slots: dict[str, Any] = {"primary": None, "secondary": None}
    for name, char in chars.items():
        if not isinstance(char, dict):
            continue
        slot = char.get("slot")
        if slot not in slots:
            continue
        slots[slot] = {
            "name": name,
            "locked": bool(char.get("locked")),
            "lock_source": char.get("lock_source"),
            "has_reference_image": bool(char.get("ref_image_path")),
            "ref_image_url": _ref_image_url(char.get("ref_image_path")),
            "appearance_prompt": char.get("appearance_prompt", ""),
        }
    return {"characters": slots}


@router.post("/{project_id}/characters/{slot}")
async def upload_character_reference(
    project_id: uuid.UUID,
    slot: Literal["primary", "secondary"],
    name: str = Form(...),
    appearance_prompt: str = Form(""),
    image: UploadFile = File(...),
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """
    Uploads and locks a character's reference image to a named slot.
    "primary" is the protagonist; "secondary" is optional (e.g. a sidekick
    or antagonist). Locking is immediate — no separate lock/unlock step
    needed for the common case of "here's the character's photo, use it".

    Every shot the storyboard tags with this exact character name will be
    rendered with i2v conditioned on this image (see routing.py) and
    checked for identity drift against it (see visual_critic.py).
    """
    await _get_project_or_404(project_id, db)

    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    if slot not in _ALLOWED_SLOTS:
        raise HTTPException(status_code=400, detail=f"slot must be one of {sorted(_ALLOWED_SLOTS)}")

    ext = _ALLOWED_CONTENT_TYPES.get(image.content_type or "")
    if not ext:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type {image.content_type!r}; use PNG, JPEG, or WEBP",
        )

    data = await image.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded image is empty")
    if len(data) > _MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="Image too large (max 8MB)")

    char_dir = MEDIA_DIR / "characters" / str(project_id)
    char_dir.mkdir(parents=True, exist_ok=True)
    dest = char_dir / f"{slot}{ext}"
    dest.write_bytes(data)

    service = SeriesBibleService(db=db)
    char = await service.set_character_slot(
        project_id=project_id,
        slot=slot,
        name=name,
        ref_image_path=str(dest),
        appearance_prompt=appearance_prompt.strip(),
    )
    logger.info("Locked character %r into slot %s for project %s", name, slot, project_id)

    return {
        "slot": slot,
        "name": name,
        "locked": True,
        "lock_source": char.get("lock_source"),
        "ref_image_url": _ref_image_url(char.get("ref_image_path")),
    }


@router.delete("/{project_id}/characters/{slot}")
async def unlock_character_slot(
    project_id: uuid.UUID,
    slot: Literal["primary", "secondary"],
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """Unlocks (but does not delete) whichever character currently occupies
    this slot — future shots for that name stop being anchored to a
    reference image until it's re-uploaded or re-bootstrapped."""
    await _get_project_or_404(project_id, db)
    service = SeriesBibleService(db=db)
    occupant = await service.get_character_by_slot(project_id, slot)
    if occupant is None:
        raise HTTPException(status_code=404, detail=f"No character is currently assigned to slot {slot!r}")

    name, _char = occupant
    await service.unlock_character(project_id, name)
    return {"slot": slot, "name": name, "locked": False}
