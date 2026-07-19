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

from showrunner_api.config import get_settings
from showrunner_api.infra.neo4j_driver import neo4j_client
from showrunner_api.routers import campaigns, gate, health, me, webhooks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Log configuration on startup
    settings = get_settings()
    logger.info(f"Starting Convertale API v{settings.app_version} in {settings.app_env} mode")
    
    # Verify Qwen configuration
    if settings.qwen_api_key or settings.dashscope_api_key:
        key_type = "workspace" if (settings.qwen_api_key or settings.dashscope_api_key).startswith("sk-ws-") else "standard"
        logger.info(f"Qwen/DashScope configured with {key_type} key")
        logger.info(f"Base URL: {settings.qwen_base_url}")
    else:
        logger.warning("⚠️  No Qwen/DashScope API key configured - LLM features will use stub responses")
    
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

    return app


app = create_app()
