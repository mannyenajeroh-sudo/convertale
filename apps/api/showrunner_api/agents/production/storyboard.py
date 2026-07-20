import json
import uuid
from typing import Any

from showrunner_api.agents.base import BaseAgent
from showrunner_api.llm_client import MAX_VIDEO_DURATION_SEC, MIN_VIDEO_DURATION_SEC, call_qwen


class StoryboardAgent(BaseAgent):
    """Breaks down an episode synopsis into a detailed shot list.

    Two things layered on top of the original break-down:
      1. Variable, director-style shot pacing. wan2.6-t2v/i2v both take a
         real per-shot duration (2-15s) — see llm_client.clamp_duration —
         so this agent now explicitly asks for unconventional rhythm
         (punchy 2-3s cuts mixed with held 8-12s beats) instead of letting
         every shot default to a flat 5s, which is what made prior output
         read as a slideshow of independent clips rather than a directed
         scene.
      2. Locked-character tagging. If the caller passes `locked_characters`
         (names currently locked in the SeriesBible — see pipeline.py), the
         model is told to use those exact names and to report which of them
         appears in each shot via a `characters_in_shot` field. Routing.py
         uses this to decide which reference image(s) to condition i2v on
         and which to hand the Visual Critic — without it, there'd be no
         way to know which locked character(s), if any, a given shot needs
         to stay consistent with.
    """

    async def run(self, input_json: dict[str, Any]) -> dict[str, Any]:
        workspace_id = uuid.UUID(input_json["_workspace_id"])
        project_id = uuid.UUID(input_json["_project_id"]) if "_project_id" in input_json else None

        episode_synopsis = input_json.get("synopsis", "")
        if not episode_synopsis:
            return {"error": "synopsis is required"}

        locked_characters: list[str] = [c for c in input_json.get("locked_characters", []) if c]

        character_instruction = ""
        if locked_characters:
            names = ", ".join(f'"{n}"' for n in locked_characters)
            character_instruction = (
                f"\nThe following character name(s) are visually locked for this series: {names}. "
                "Use these EXACT names whenever one of them appears — never rename or re-describe "
                "them differently between shots. For every shot, also return a "
                "'characters_in_shot' field: a JSON array containing whichever of these exact "
                "names physically appear on-screen in that shot (empty array if none do)."
            )

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
            "You are a master storyboard artist and director for short B2B narrative video ads, "
            "in the tradition of directors who vary shot length deliberately to control pacing — "
            "quick cuts for urgency, held shots for emotional weight — rather than cutting every "
            "shot to the same length like a slideshow. "
            "Break the provided synopsis into a sequential list of shots. "
            "For each shot, return ALL of the following fields: "
            "'shot_number' (int), 'camera_angle' (string), 'action' (string), "
            "'dialogue' (string, empty string if none), "
            f"'estimated_duration_sec' (number, an INTEGER between {MIN_VIDEO_DURATION_SEC} and "
            f"{MAX_VIDEO_DURATION_SEC} — vary this deliberately across the episode: mix short "
            "punch-in cuts (2-3s) with longer held beats (8-12s) based on the dramatic weight of "
            "each moment, do not default every shot to the same number), and "
            "'visual_prompt' (string) — a standalone, richly detailed, cinematic description of "
            "exactly what should appear on screen in this shot, written for a text-to-video "
            "generation model. 'visual_prompt' MUST always be a non-empty string containing at "
            "least one full descriptive sentence — never omit it and never leave it blank, even "
            "for simple shots. It should describe subject, setting, lighting, and camera motion "
            "in concrete visual terms; do not just repeat the 'action' field verbatim."
            f"{character_instruction}\n"
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

        if isinstance(parsed_response, dict) and isinstance(parsed_response.get("shots"), list):
            shots = [s for s in parsed_response["shots"] if isinstance(s, dict)]

            # FIXED: belt-and-suspenders backstop for the same issue — even
            # with the stricter prompt above, LLM output is never a
            # guaranteed contract. If a shot still comes back with a
            # missing/blank visual_prompt, synthesize one from the fields we
            # DO require (camera_angle + action + dialogue) rather than
            # silently letting an empty string reach the video API later and
            # fail with "prompt must contain words".
            for shot in shots:
                vp = shot.get("visual_prompt")
                if not vp or not str(vp).strip():
                    shot["visual_prompt"] = _fallback_visual_prompt(shot)

                shot["duration_sec"] = _clamp_duration(shot.get("estimated_duration_sec"))

                if locked_characters:
                    raw_names = shot.get("characters_in_shot")
                    if isinstance(raw_names, list):
                        # Only keep names that actually match a locked
                        # character — an LLM inventing/misspelling a name
                        # here would otherwise silently fail to match
                        # anything downstream in routing.py.
                        shot["characters_in_shot"] = [n for n in raw_names if n in locked_characters]
                    else:
                        shot["characters_in_shot"] = []
                else:
                    shot.setdefault("characters_in_shot", [])

            # Deterministic, zero-token rhythm guardrail: if the model
            # ignored the pacing instruction and returned the same duration
            # for every shot (the exact "slideshow" failure mode this
            # feature exists to prevent), nudge durations into an
            # alternating short/long pattern rather than spending another
            # LLM call to re-ask for variety. Only kicks in when genuinely
            # flat — a model that already varied durations is left alone.
            durations = [s["duration_sec"] for s in shots]
            if len(durations) >= 3 and len(set(durations)) == 1:
                base = durations[0]
                pattern = [-2, 0, 3, -1, 2, 0]
                for i, shot in enumerate(shots):
                    shot["duration_sec"] = _clamp_duration(base + pattern[i % len(pattern)])

            parsed_response["shots"] = shots

        approx_tokens = (len(system_prompt) + len(user_prompt) + len(response_text)) // 4
        await self.record_usage(
            workspace_id=workspace_id,
            project_id=project_id,
            model="qwen-max",
            tokens=approx_tokens
        )

        return parsed_response


def _clamp_duration(value: Any) -> int:
    try:
        d = round(float(value))
    except (TypeError, ValueError):
        return 5
    return max(MIN_VIDEO_DURATION_SEC, min(MAX_VIDEO_DURATION_SEC, d))


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
