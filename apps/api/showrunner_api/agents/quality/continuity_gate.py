import json
import uuid
from typing import Any

from showrunner_api.agents.base import BaseAgent
from showrunner_api.llm_client import call_qwen


class ContinuityGateAgent(BaseAgent):
    """Checks for narrative continuity issues."""

    async def run(self, input_json: dict[str, Any]) -> dict[str, Any]:
        workspace_id = uuid.UUID(input_json["_workspace_id"])
        project_id = uuid.UUID(input_json["_project_id"]) if "_project_id" in input_json else None
        
        episodes = input_json.get("episodes", [])
        if not episodes:
            return {"error": "episodes are required for continuity check"}
            
        facts = "No external facts provided."
        # If neo4j graph memory is configured, we could pull established facts
        if self.graph:
            try:
                # Attempt to get some context, if implemented
                # facts = await self.graph.get_world_context(str(project_id))
                pass
            except Exception:
                pass

        system_prompt = (
            "You are a strict continuity editor. Review the provided episodes and established facts. "
            "Identify any contradictions between episodes or violations of established rules. "
            "Return a JSON object with a boolean 'passed' and a list of 'issues' (strings). "
            "If passed is true, issues should be empty."
        )
        
        user_prompt = f"Facts:\n{facts}\n\nEpisodes:\n{json.dumps(episodes, indent=2)}"
        
        response_text = await call_qwen(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model="qwen-plus",  # balanced model
            json_mode=True
        )
        
        try:
            parsed_response = json.loads(response_text)
        except json.JSONDecodeError:
            parsed_response = {"passed": False, "issues": ["Failed to parse LLM response.", response_text]}
            
        approx_tokens = (len(system_prompt) + len(user_prompt) + len(response_text)) // 4
        await self.record_usage(
            workspace_id=workspace_id,
            project_id=project_id,
            model="qwen-plus",
            tokens=approx_tokens
        )
        
        return parsed_response
