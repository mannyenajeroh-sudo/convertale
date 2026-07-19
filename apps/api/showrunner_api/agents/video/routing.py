import asyncio
import uuid
import os
import tempfile
from typing import Any

from showrunner_api.agents.base import BaseAgent
from showrunner_api.agents.quality.visual_critic import VisualCriticAgent
from showrunner_api.llm_client import generate_video_t2v, download_file


def _fallback_visual_prompt(shot: dict[str, Any]) -> str:
    """Build a guaranteed non-empty T2V prompt from whatever fields a shot
    does have. Mirrors the fallback in storyboard.py — kept here too since
    this agent must never hand the video API an empty prompt regardless of
    what upstream produced."""
    camera_angle = str(shot.get("camera_angle") or "").strip()
    action = str(shot.get("action") or "").strip()
    dialogue = str(shot.get("dialogue") or "").strip()

    parts = []
    if camera_angle:
        parts.append(f"{camera_angle} shot")
    if action:
        parts.append(action)
    if dialogue:
        parts.append(f'Character says: "{dialogue}"')

    if parts:
        return ". ".join(parts) + "."

    return "Cinematic B2B narrative advertisement shot, well-lit, dynamic camera movement."


class VideoRoutingAgent(BaseAgent):
    """
    Dispatches to video generators based on shot type.
    Includes the Critic-Optimizer loop for character consistency.
    """

    async def _render_with_retry(
        self,
        shot: dict[str, Any],
        critic: VisualCriticAgent,
        reference_clip_path: str | None,
        job_dir: str
    ) -> dict[str, Any]:
        # FIXED: was `shot.get("prompt", "")` — StoryboardAgent never
        # produced a "prompt" field at all (only shot_number, camera_angle,
        # action, dialogue, estimated_duration_sec), so this silently sent
        # an empty string to the video model whenever the LLM didn't
        # spontaneously include one, causing Wan's
        # "InvalidParameter: prompt must contain words" on that shot.
        # StoryboardAgent now explicitly requests + guarantees a
        # "visual_prompt" field (see storyboard.py); read that here, with
        # the same synthesis-from-other-fields fallback as a second safety
        # net in case a shot dict ever reaches this agent from somewhere
        # else that doesn't go through StoryboardAgent's guarantee.
        prompt = shot.get("visual_prompt") or _fallback_visual_prompt(shot)
        max_retries = 3
        attempts = 0
        best_clip = None
        best_score = 0.0
        engine = "Wan (Qwen Cloud)"  # FIXED: default so it's always defined even if the loop body changes later

        while attempts < max_retries:
            attempts += 1
            # 1. Render
            if shot.get("dialogue"):
                # Stub HappyHorse for now if dialogue, Wan doesn't do lip-sync well
                engine = "HappyHorse (Fal.ai)"
                clip_url = f"https://example.com/stub_happyhorse_{uuid.uuid4().hex[:8]}.mp4"
            else:
                engine = "Wan (Qwen Cloud)"
                clip_url = await generate_video_t2v(
                    prompt=prompt,
                    size="720*1280",
                    duration=5
                )

            dest = os.path.join(job_dir, f"shot_{shot.get('shot_number', 0)}_{attempts}.mp4")
            if "example.com" not in clip_url:
                clip_path = str(await download_file(clip_url, dest))
            else:
                # Mock download for stub
                with open(dest, "w") as f:
                    f.write("mock")
                clip_path = dest

            # 2. Critique
            verdict = await critic.evaluate_clip(
                description=shot.get("action", ""),
                prompt=prompt,
                clip_path=clip_path,
                reference_clip_path=reference_clip_path,
                threshold=0.6
            )

            score = verdict["score"]
            if score > best_score or best_clip is None:
                best_score = score
                best_clip = clip_path

            if verdict["passed"]:
                return {
                    "shot_number": shot.get("shot_number"),
                    "engine_used": engine,
                    "clip_path": clip_path,
                    "score": score,
                    "attempts": attempts,
                    "passed": True,
                }

            # Optimizer rewriting
            if verdict["revised_prompt"]:
                prompt = verdict["revised_prompt"]

        # FIXED: previously this could return clip_path=None if every attempt
        # failed to extract a frame/produce a clip at all (best_clip stays None).
        # assembly.py does Path(clip["clip_path"]) unconditionally and would
        # crash on that. We now guarantee a path (falling back to the last
        # attempted clip) and flag the shot as not passed so callers can decide
        # whether to proceed, retry the whole shot, or surface it to the user.
        return {
            "shot_number": shot.get("shot_number"),
            "engine_used": engine,
            "clip_path": best_clip if best_clip is not None else clip_path,
            "score": best_score,
            "attempts": attempts,
            "passed": False,
        }

    async def run(self, input_json: dict[str, Any]) -> dict[str, Any]:
        # workspace_id / project_id are used by BaseAgent.execute() for job
        # tracking; this method itself doesn't need them directly.
        _workspace_id = uuid.UUID(input_json["_workspace_id"])
        _project_id = uuid.UUID(input_json["_project_id"]) if "_project_id" in input_json else None

        shots = input_json.get("shots", [])
        if not shots:
            return {"error": "shots list is required"}

        critic = VisualCriticAgent(db=self.db, graph=self.graph, mcp=self.mcp, token_budget=self.token_budget)

        job_dir = tempfile.mkdtemp(prefix="convertale_job_")

        # Parallelize rendering
        tasks = []
        # For simplicity, no reference clip passed here. In a real scenario, we'd pass a locked character reference.
        reference_clip_path = input_json.get("reference_clip_path")

        for shot in shots:
            tasks.append(self._render_with_retry(shot, critic, reference_clip_path, job_dir))

        generated_clips = await asyncio.gather(*tasks)

        failed_shots = [c for c in generated_clips if not c.get("passed", True)]
        if failed_shots:
            # Don't silently hand these to AssemblyAgent as if they were fine —
            # at minimum surface which shots never passed the continuity critic.
            shot_numbers = [c.get("shot_number") for c in failed_shots]
            return {
                "clips": generated_clips,
                "status": "completed_with_warnings",
                "job_dir": job_dir,
                "failed_shot_numbers": shot_numbers,
            }

        return {"clips": generated_clips, "status": "completed", "job_dir": job_dir}
