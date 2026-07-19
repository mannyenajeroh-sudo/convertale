from fastapi import APIRouter, Response, status

from showrunner_api.config import get_settings
from showrunner_api.infra.db import check_database
from showrunner_api.infra.neo4j_driver import neo4j_client

router = APIRouter()


@router.get("/health")
async def health(response: Response) -> dict[str, str]:
    settings = get_settings()
    checks: dict[str, str] = {"status": "ok", "version": settings.app_version}

    try:
        await check_database()
        checks["neon_db"] = "connected"
    except Exception:
        checks["neon_db"] = "unreachable"
        checks["status"] = "degraded"

    try:
        await neo4j_client.verify_connectivity()
        checks["neo4j_aura"] = "connected"
    except Exception:
        checks["neo4j_aura"] = "unreachable"
        checks["status"] = "degraded"

    # Only return 503 Service Unavailable if the primary SQL database is unreachable.
    # An unreachable Neo4j AuraDB is allowed to run in stub/degraded mode.
    if checks.get("neon_db") == "unreachable":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return checks
