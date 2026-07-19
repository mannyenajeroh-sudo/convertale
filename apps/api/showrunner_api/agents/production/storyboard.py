import json
import uuid
from typing import Any

from showrunner_api.agents.base import BaseAgent
from showrunner_api.llm_client import call_qwen


class StoryboardAgent(BaseAgent):
    """Breaks down an episode synopsis into a detailed shot list."""

    async def run(self, input_json: dict[str, Any]) -> dict[str, Any]:
        workspace_id = uuid.UUID(input_json["_workspace_id"])
        project_id = uuid.UUID(input_json["_project_id"]) if "_project_id" in input_json else None
        
        episode_synopsis = input_json.get("synopsis", "")
        if not episode_synopsis:
            return {"error": "synopsis is required"}
            
        system_prompt = (
            "You are a master storyboard artist and director for short B2B narrative video ads. "
            "Break the provided synopsis into a sequential list of shots. "
            "For each shot, specify 'shot_number', 'camera_angle', 'action', 'dialogue' (if any), and 'estimated_duration_sec'. "
            "Keep the shots punchy and dynamic. "
            "Return a JSON object containing a 'shots' array."
        )
        
        user_prompt = f"Synopsis:\n{episode_synopsis}"
        
        response_text = await call_qwen(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model="qwen-max",
            json_mode=True
        )
        
        try:
            parsed_response = json.loads(response_text)
        except json.JSONDecodeError:
            parsed_response = {"raw_storyboard": response_text}
            
        approx_tokens = (len(system_prompt) + len(user_prompt) + len(response_text)) // 4
        await self.record_usage(
            workspace_id=workspace_id,
            project_id=project_id,
            model="qwen-max",
            tokens=approx_tokens
        )
        
        return parsed_response
