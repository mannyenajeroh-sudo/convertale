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

        # FIXED: routing.py builds each shot's text-to-video request from
        # shot.get("prompt", ""), but this system prompt never asked the
        # model for a "prompt" field at all — only shot_number,
        # camera_angle, action, dialogue, estimated_duration_sec. Whether a
        # shot happened to include one was pure LLM whim, not a guaranteed
        # contract, which is why it worked most of the time and then failed
        # with Wan's "prompt must contain words" on whichever shot the model
        # omitted it from. Now explicitly requesting a dedicated
        # "visual_prompt" field — a self-contained, cinematic description
        # written specifically for a text-to-video model, distinct from the
        # structured shot-breakdown fields used elsewhere in the pipeline
        # (continuity checking, subtitle timing, etc).
        system_prompt = (
            "You are a master storyboard artist and director for short B2B narrative video ads. "
            "Break the provided synopsis into a sequential list of shots. "
            "For each shot, return ALL of the following fields: "
            "'shot_number' (int), 'camera_angle' (string), 'action' (string), "
            "'dialogue' (string, empty string if none), 'estimated_duration_sec' (number), and "
            "'visual_prompt' (string) — a standalone, richly detailed, cinematic description of "
            "exactly what should appear on screen in this shot, written for a text-to-video "
            "generation model. 'visual_prompt' MUST always be a non-empty string containing at "
            "least one full descriptive sentence — never omit it and never leave it blank, even "
            "for simple shots. It should describe subject, setting, lighting, and camera motion "
            "in concrete visual terms; do not just repeat the 'action' field verbatim. "
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

        # FIXED: belt-and-suspenders backstop for the same issue — even with
        # the stricter prompt above, LLM output is never a guaranteed
        # contract. If a shot still comes back with a missing/blank
        # visual_prompt, synthesize one from the fields we DO require
        # (camera_angle + action + dialogue) rather than silently letting an
        # empty string reach the video API later and fail with
        # "prompt must contain words".
        if isinstance(parsed_response, dict) and isinstance(parsed_response.get("shots"), list):
            for shot in parsed_response["shots"]:
                if not isinstance(shot, dict):
                    continue
                vp = shot.get("visual_prompt")
                if not vp or not str(vp).strip():
                    shot["visual_prompt"] = _fallback_visual_prompt(shot)

        approx_tokens = (len(system_prompt) + len(user_prompt) + len(response_text)) // 4
        await self.record_usage(
            workspace_id=workspace_id,
            project_id=project_id,
            model="qwen-max",
            tokens=approx_tokens
        )

        return parsed_response


def _fallback_visual_prompt(shot: dict[str, Any]) -> str:
    """Build a guaranteed non-empty T2V prompt from whatever fields a shot does have."""
    camera_angle = str(shot.get("camera_angle") or "").strip()
    action = str(shot.get("action") or "").strip()
    dialogue = str(shot.get("dialogue") or "").strip()

    parts = []
    if camera_angle:
        parts.append(f"{camera_angle} shot")
    if action:
        parts.append(action)
    if dialogue:
        parts.append(f"Character says: \"{dialogue}\"")

    if parts:
        return ". ".join(parts) + "."

    # Last-resort generic fallback so the video API never receives an
    # empty/whitespace-only prompt, even if the LLM returned a near-empty
    # shot dict.
    return "Cinematic B2B narrative advertisement shot, well-lit, dynamic camera movement."
