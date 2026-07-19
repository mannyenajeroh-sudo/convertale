"""Base class for all pipeline agents.

Every concrete agent (BrandBriefIntakeAgent, WritersRoomAgent, StoryboardAgent,
etc.) subclasses ``BaseAgent`` and implements ``run()``. ``BaseAgent`` supplies
the shared plumbing every agent needs:

  * dependency injection for the DB session, graph-memory service, MCP
    registry, and token-budget manager
  * an ``AgentJob`` audit row per invocation (pending -> running -> success/error)
  * usage/token recording for cost accounting
"""

from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from showrunner_api.models import AgentJob, UsageRecord
from showrunner_api.services.graph_memory import GraphMemoryService
from showrunner_api.services.mcp_registry import EmptyMCPRegistry, MCPRegistry
from showrunner_api.services.token_budget import TokenBudgetManager

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Shared template-method base for every pipeline agent.

    Subclasses implement :meth:`run`. Callers should invoke :meth:`execute`,
    which wraps ``run()`` with job tracking, error handling, and commits.
    """

    def __init__(
        self,
        db: AsyncSession,
        graph: GraphMemoryService | None = None,
        mcp: MCPRegistry | None = None,
        token_budget: TokenBudgetManager | None = None,
    ) -> None:
        self.db = db
        self.graph = graph if graph is not None else GraphMemoryService()
        self.mcp = mcp if mcp is not None else EmptyMCPRegistry()
        self.token_budget = token_budget if token_budget is not None else TokenBudgetManager()

    @property
    def agent_name(self) -> str:
        return type(self).__name__

    @abstractmethod
    async def run(self, input_json: dict[str, Any]) -> dict[str, Any]:
        """Agent-specific logic. Implemented by subclasses."""
        raise NotImplementedError

    async def execute(
        self,
        project_id: uuid.UUID,
        workspace_id: uuid.UUID,
        input_json: dict[str, Any],
        episode_id: uuid.UUID | None = None,
    ) -> dict[str, Any]:
        """Run the agent with job tracking, then return its result.

        Creates an ``AgentJob`` row up front (status="running"), invokes
        ``run()``, and marks the job "success" or "error" depending on the
        outcome. Re-raises any exception from ``run()`` after recording it,
        so callers can decide how to handle pipeline failures.
        """
        job = AgentJob(
            project_id=project_id,
            episode_id=episode_id,
            agent_name=self.agent_name,
            status="running",
            input_json=input_json,
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(job)

        # FIXED: this commit previously wasn't guarded. If it fails — most
        # commonly a FK violation because episode_id was handed to us without
        # a matching Episode row actually existing yet (see WritersRoomAgent)
        # — the exception used to propagate with the session left mid-failed
        # transaction. Since pipeline.py reuses one `db` session across every
        # agent/episode in the loop, every *subsequent* episode would then
        # also fail, with a confusing secondary error masking the real cause.
        # Roll back explicitly so the session is usable again and the error
        # that surfaces is the actual root cause.
        try:
            await self.db.commit()
            await self.db.refresh(job)
        except Exception:
            await self.db.rollback()
            logger.exception(
                "Agent %s: failed to create AgentJob row (project=%s, episode=%s). "
                "If episode_id is set, verify that episode actually exists and "
                "was committed by a prior agent before this one ran.",
                self.agent_name, project_id, episode_id,
            )
            raise

        # Give subclasses access to caller context without changing every
        # agent's method signature.
        enriched_input = {
            **input_json,
            "_project_id": str(project_id),
            "_workspace_id": str(workspace_id),
        }

        try:
            result = await self.run(enriched_input)
        except Exception as exc:
            job.status = "error"
            job.error_text = str(exc)
            job.completed_at = datetime.now(timezone.utc)
            try:
                await self.db.commit()
            except Exception:
                # If even the error-status commit fails, don't let that mask
                # the original exception — roll back and let the original
                # propagate.
                await self.db.rollback()
                logger.exception(
                    "Agent %s: failed to record error status for job %s", self.agent_name, job.id
                )
            logger.exception("Agent %s failed for project %s", self.agent_name, project_id)
            raise

        job.status = "error" if isinstance(result, dict) and "error" in result else "success"
        job.output_json = result
        job.completed_at = datetime.now(timezone.utc)
        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            logger.exception(
                "Agent %s: failed to commit final job status for job %s", self.agent_name, job.id
            )
            raise
        return result

    async def record_usage(
        self,
        workspace_id: uuid.UUID,
        project_id: uuid.UUID | None,
        model: str,
        tokens: int,
    ) -> None:
        """Record LLM token usage for cost accounting / budget enforcement."""
        self.db.add(
            UsageRecord(
                workspace_id=workspace_id,
                project_id=project_id,
                record_type="llm_tokens",
                quantity=tokens,
                model=model,
            )
        )
        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            logger.exception("Agent %s: failed to commit usage record", self.agent_name)
            raise
