import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from showrunner_api.agents.production.assembly import BACKEND_BASE_URL, MEDIA_DIR
from showrunner_api.auth import AuthenticatedUser, get_current_user
from showrunner_api.infra.db import get_session
from showrunner_api.models import Project

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["brand-assets"])

# PNG/WEBP preferred (alpha channel survives the watermark's own
# transparency blend cleanly); JPEG accepted too since a lot of brand kits
# only have a JPEG logo on hand.
_ALLOWED_CONTENT_TYPES = {"image/png": ".png", "image/webp": ".webp", "image/jpeg": ".jpg"}
_MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5MB


async def _get_project_or_404(project_id: uuid.UUID, db: AsyncSession) -> Project:
    project = (await db.execute(select(Project).where(Project.id == project_id))).scalars().first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _logo_url(project_id: uuid.UUID, ext: str) -> str:
    return f"{BACKEND_BASE_URL}/media/logos/{project_id}{ext}"


@router.get("/{project_id}/logo")
async def get_logo(
    project_id: uuid.UUID,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    project = await _get_project_or_404(project_id, db)
    if not project.brand_logo_path:
        return {"logo_url": None}
    from pathlib import Path
    ext = Path(project.brand_logo_path).suffix
    return {"logo_url": _logo_url(project_id, ext)}


@router.post("/{project_id}/logo")
async def upload_logo(
    project_id: uuid.UUID,
    logo: UploadFile = File(...),
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    """
    Uploads the project's brand logo. Every episode assembled after this is
    set will have it tastefully composited as a small, semi-transparent
    corner watermark (see AssemblyAgent._LOGO_* constants) — burned in
    alongside the subtitles in a single ffmpeg pass, not as a separate
    always-on overlay layer the user has to manage per-shot.

    Re-uploading replaces the existing logo. There's no separate "enable/
    disable watermark" toggle: DELETE this endpoint to remove it.
    """
    project = await _get_project_or_404(project_id, db)

    ext = _ALLOWED_CONTENT_TYPES.get(logo.content_type or "")
    if not ext:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type {logo.content_type!r}; use PNG, WEBP, or JPEG",
        )

    data = await logo.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded logo is empty")
    if len(data) > _MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="Logo too large (max 5MB)")

    logo_dir = MEDIA_DIR / "logos"
    logo_dir.mkdir(parents=True, exist_ok=True)

    # Clean up a previous logo saved under a different extension (e.g. user
    # first uploaded a .png, now uploads a .jpg) so stale files don't pile up.
    if project.brand_logo_path:
        from pathlib import Path
        old = Path(project.brand_logo_path)
        if old.exists() and old.suffix != ext:
            old.unlink(missing_ok=True)

    dest = logo_dir / f"{project_id}{ext}"
    dest.write_bytes(data)

    project.brand_logo_path = str(dest)
    await db.commit()

    logger.info("Set brand logo for project %s -> %s", project_id, dest)
    return {"logo_url": _logo_url(project_id, ext)}


@router.delete("/{project_id}/logo")
async def remove_logo(
    project_id: uuid.UUID,
    user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    project = await _get_project_or_404(project_id, db)
    if project.brand_logo_path:
        from pathlib import Path
        Path(project.brand_logo_path).unlink(missing_ok=True)
        project.brand_logo_path = None
        await db.commit()
    return {"logo_url": None}
