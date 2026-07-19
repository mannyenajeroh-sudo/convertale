import json
import logging
import uuid
from typing import Any

from sqlalchemy import select
from showrunner_api.agents.base import BaseAgent
from showrunner_api.llm_client import call_qwen
from showrunner_api.models import Episode, Project

logger = logging.getLogger(__name__)


class WritersRoomAgent(BaseAgent):
    """Generates the multi-episode Cliffhanger story arc."""

    async def run(self, input_json: dict[str, Any]) -> dict[str, Any]:
        workspace_id = uuid.UUID(input_json["_workspace_id"])
        project_id = uuid.UUID(input_json["_project_id"]) if "_project_id" in input_json else None

        structured_brief = input_json.get("structured_brief", {})
        if not structured_brief:
            return {"error": "structured_brief is required"}

        system_prompt = (
            "You are the head writer of a short-drama studio. Based on the creative brief, "
            "generate a 3-5 episode story arc that serves as a B2B ad campaign. "
            "CRITICAL: The story must have a 'Cliffhanger Capture' mechanic. Episodes 1-2 should "
            "build massive tension, leaving a massive cliffhanger before the final episode. "
            "The final episode resolves the tension and aligns with the call_to_action. "
            "Return a JSON object with 'episodes' (list of objects with 'episode_number', 'title', 'synopsis')."
        )

        user_prompt = f"Brief:\n{json.dumps(structured_brief, indent=2)}"

        response_text = await call_qwen(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model="qwen-max",
            json_mode=True
        )

        try:
            parsed_response = json.loads(response_text)
        except json.JSONDecodeError:
            parsed_response = {"raw_arc": response_text}

        approx_tokens = (len(system_prompt) + len(user_prompt) + len(response_text)) // 4
        await self.record_usage(
            workspace_id=workspace_id,
            project_id=project_id,
            model="qwen-max",
            tokens=approx_tokens
        )

        episodes_list = parsed_response.get("episodes", []) if isinstance(parsed_response, dict) else []

        if not project_id or not episodes_list:
            return parsed_response

        result = await self.db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            logger.warning("Project %s not found - skipping episode persistence", project_id)
            return parsed_response

        pending_episodes = []
        for ep_data in episodes_list:
            new_episode = Episode(
                id=uuid.uuid4(),
                project_id=project_id,
                episode_number=ep_data.get("episode_number", 0),
                title=ep_data.get("title", "Untitled"),
                outline_json={"synopsis": ep_data.get("synopsis", "")},
                status="draft",
            )
            self.db.add(new_episode)
            pending_episodes.append((ep_data, new_episode))

        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            logger.exception("Failed to commit episodes")
            return parsed_response

        saved_episodes = []
        for ep_data, episode in pending_episodes:
            ep_data["episode_id"] = str(episode.id)
            saved_episodes.append(ep_data)

        parsed_response["episodes"] = saved_episodes
        logger.info("Saved %d episodes for project %s", len(saved_episodes), project_id)

        return parsed_response
