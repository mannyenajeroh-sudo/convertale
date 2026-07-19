from fastapi import APIRouter, Depends

from showrunner_api.auth import AuthenticatedUser, get_current_user

router = APIRouter(prefix="/api")


@router.get("/me")
async def read_me(user: AuthenticatedUser = Depends(get_current_user)) -> dict[str, str | None]:
    return {"clerk_id": user.clerk_id, "email": user.email, "db_user_id": user.db_user_id}
