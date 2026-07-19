import uuid
from typing import Any

from sqlalchemy import select

from showrunner_api.agents.base import BaseAgent
from showrunner_api.models import Episode, Lead


class GateDeliveryAgent(BaseAgent):
    """
    Handles Cliffhanger Capture distribution.
    Saves a lead email, checks episode status, and returns the asset if ready.
    """

    async def run(self, input_json: dict[str, Any]) -> dict[str, Any]:
        # This agent doesn't require a strict _workspace_id since it's a public endpoint triggered,
        # but the project_id and episode_id are required.
        
        project_id_str = input_json.get("project_id")
        episode_id_str = input_json.get("episode_id")
        email = input_json.get("email")
        
        if not all([project_id_str, episode_id_str, email]):
            return {"error": "project_id, episode_id, and email are required"}
            
        try:
            project_id = uuid.UUID(project_id_str)
            episode_id = uuid.UUID(episode_id_str)
        except ValueError:
            return {"error": "invalid UUID format"}
            
        # 1. Fetch the episode to verify it exists and get status
        result = await self.db.execute(select(Episode).where(Episode.id == episode_id, Episode.project_id == project_id))
        episode = result.scalars().first()
        
        if not episode:
            return {"error": "episode not found"}
            
        # 2. Record the lead
        lead = Lead(
            project_id=project_id,
            episode_id=episode_id,
            email=email
        )
        self.db.add(lead)
        # Flush to get lead ID if we need it
        await self.db.flush()
        
        # 3. Return outcome based on episode status
        if episode.status == "completed" and episode.assembled_video_url:
            return {
                "status": "delivered",
                "lead_id": str(lead.id),
                "video_url": episode.assembled_video_url
            }
        else:
            return {
                "status": "processing",
                "lead_id": str(lead.id),
                "message": "The episode is still being processed and will be delivered via email once ready."
            }
