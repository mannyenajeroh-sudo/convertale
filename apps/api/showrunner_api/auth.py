from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from showrunner_api.config import get_settings
from showrunner_api.infra.db import get_session
from showrunner_api.models import User

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthenticatedUser:
    clerk_id: str
    email: str | None
    db_user_id: str


def _decode_token(token: str) -> dict:
    settings = get_settings()
    if not settings.clerk_jwks_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Clerk JWKS URL is not configured",
        )

    jwk_client = PyJWKClient(settings.clerk_jwks_url)
    signing_key = jwk_client.get_signing_key_from_jwt(token)
    options = {"verify_aud": bool(settings.clerk_jwt_audience)}
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.clerk_jwt_audience or None,
        issuer=settings.clerk_issuer or None,
        options=options,
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: AsyncSession = Depends(get_session),
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    try:
        claims = _decode_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    clerk_id = claims.get("sub")
    if not clerk_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing subject")

    email = claims.get("email")
    result = await session.execute(select(User).where(User.clerk_id == clerk_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(clerk_id=clerk_id, email=email, plan="free")
        session.add(user)
        try:
            await session.commit()
        except IntegrityError:
            # Another concurrent request for the same brand-new clerk_id
            # won the race and already inserted the row. Roll back this
            # attempt and re-fetch instead of surfacing a 500.
            await session.rollback()
            result = await session.execute(select(User).where(User.clerk_id == clerk_id))
            user = result.scalar_one()
    elif email and user.email != email:
        user.email = email
        await session.commit()

    return AuthenticatedUser(clerk_id=clerk_id, email=email, db_user_id=str(user.id))


def is_public_path(request: Request) -> bool:
    return request.url.path in {"/health", "/docs", "/openapi.json", "/api/webhooks/clerk"}
