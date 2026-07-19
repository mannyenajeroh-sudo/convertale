import json
import uuid
from typing import Any

from showrunner_api.agents.base import BaseAgent
from showrunner_api.llm_client import call_qwen


class BrandBriefIntakeAgent(BaseAgent):
    """Parses raw brand brief into structured creative brief."""
    
    async def run(self, input_json: dict[str, Any]) -> dict[str, Any]:
        workspace_id = uuid.UUID(input_json["_workspace_id"])
        project_id = uuid.UUID(input_json["_project_id"]) if "_project_id" in input_json else None
        
        raw_brief = input_json.get("raw_brief", "")
        if not raw_brief:
            return {"error": "raw_brief is required"}
            
        system_prompt = (
            "You are an expert creative strategist. Extract the following from the raw brief: "
            "product, target_audience, tone, key_message, call_to_action. "
            "Return the output STRICTLY as a JSON object."
        )
        
        user_prompt = f"Raw brief:\n{raw_brief}"
        
        # Call LLM
        response_text = await call_qwen(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model="qwen-max",
            json_mode=True
        )
        
        try:
            parsed_response = json.loads(response_text)
        except json.JSONDecodeError:
            parsed_response = {"extracted_text": response_text}
            
        # Estimate tokens for budget recording
        approx_tokens = (len(system_prompt) + len(user_prompt) + len(response_text)) // 4
        await self.record_usage(
            workspace_id=workspace_id,
            project_id=project_id,
            model="qwen-max",
            tokens=approx_tokens
        )
        
        return parsed_response
