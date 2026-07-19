"""FastAPI application factory / entrypoint.

This module previously did not exist. The Dockerfile has always run
``uvicorn showrunner_api.main:app`` and the Helm chart expects the same, but
the only ``main.py`` in the repository lived at ``apps/api/main.py`` — a
disconnected two-line stub (``FastAPI()`` + a bare ``/health`` route) that
was never copied into the Docker image and never included any of the real
routers. The container would crash on startup with
``ModuleNotFoundError: No module named 'showrunner_api.main'``, and even if
that path had existed, none of ``campaigns``, ``gate``, ``me``, or
``webhooks`` were ever wired up anywhere in the codebase.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from showrunner_api.agents.production.assembly import MEDIA_DIR
from showrunner_api.config import get_settings
from showrunner_api.infra.neo4j_driver import neo4j_client
from showrunner_api.routers import campaigns, gate, health, me, webhooks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Cleanly release the Neo4j driver's connection pool on shutdown.
    await neo4j_client.close()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Convertale API",
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(me.router)
    app.include_router(campaigns.router)
    app.include_router(gate.router)
    app.include_router(webhooks.router)

    # FIXED: AssemblyAgent now writes finished episode MP4s to MEDIA_DIR and
    # builds real "http://localhost:8000/media/<file>" URLs for them (see
    # assembly.py), but nothing was ever mounting that directory — so those
    # URLs 404'd instead of serving anything. This is why the dashboard
    # still showed no playable video even after the URL stopped being a
    # stub example.com link.
    app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

    return app


app = create_app()
