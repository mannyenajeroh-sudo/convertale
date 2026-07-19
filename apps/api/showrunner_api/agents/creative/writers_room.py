import json
import uuid
from typing import Any

from showrunner_api.agents.base import BaseAgent
from showrunner_api.llm_client import call_qwen


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
        
        return parsed_response
