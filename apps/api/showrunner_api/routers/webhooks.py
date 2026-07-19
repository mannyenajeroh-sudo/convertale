
from fastapi import APIRouter, Header, HTTPException, Request, status
from sqlalchemy import select
from svix.webhooks import Webhook, WebhookVerificationError

from showrunner_api.config import get_settings
from showrunner_api.infra.db import SessionLocal
from showrunner_api.models import ClerkWebhookEvent, User, Workspace

router = APIRouter(prefix="/api/webhooks")


def _primary_email(data: dict) -> str | None:
    emails = data.get("email_addresses") or []
    primary_id = data.get("primary_email_address_id")
    for item in emails:
        if item.get("id") == primary_id:
            return item.get("email_address")
    return emails[0].get("email_address") if emails else None


@router.post("/clerk")
async def clerk_webhook(
    request: Request,
    svix_id: str | None = Header(default=None),
    svix_timestamp: str | None = Header(default=None),
    svix_signature: str | None = Header(default=None),
) -> dict[str, bool]:
    settings = get_settings()
    if not settings.clerk_webhook_signing_secret:
        raise HTTPException(status_code=503, detail="Clerk webhook signing secret is not configured")

    body = await request.body()
    headers = {
        "svix-id": svix_id or "",
        "svix-timestamp": svix_timestamp or "",
        "svix-signature": svix_signature or "",
    }
    try:
        event = Webhook(settings.clerk_webhook_signing_secret).verify(body, headers)
    except WebhookVerificationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature") from exc

    event_id = event.get("id")
    event_type = event.get("type")
    data = event.get("data") or {}
    if not event_id or not event_type:
        raise HTTPException(status_code=400, detail="Malformed Clerk event")

    async with SessionLocal() as session:
        existing = await session.get(ClerkWebhookEvent, event_id)
        if existing:
            return {"received": True}

        if event_type in {"user.created", "user.updated"}:
            clerk_id = data["id"]
            result = await session.execute(select(User).where(User.clerk_id == clerk_id))
            user = result.scalar_one_or_none()
            if user is None:
                user = User(clerk_id=clerk_id, email=_primary_email(data), plan="free")
                session.add(user)
            else:
                user.email = _primary_email(data)

        if event_type in {"organization.created", "organization.updated"}:
            clerk_org_id = data["id"]
            result = await session.execute(
                select(Workspace).where(Workspace.clerk_org_id == clerk_org_id)
            )
            workspace = result.scalar_one_or_none()
            if workspace is None:
                workspace = Workspace(clerk_org_id=clerk_org_id, name=data.get("name") or "Workspace")
                session.add(workspace)
            else:
                workspace.name = data.get("name") or workspace.name

        session.add(ClerkWebhookEvent(id=event_id, event_type=event_type))
        await session.commit()

    return {"received": True}
