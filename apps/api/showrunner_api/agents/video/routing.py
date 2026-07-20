import asyncio
import logging
import uuid
import os
import tempfile
from typing import Any

from showrunner_api.agents.base import BaseAgent
from showrunner_api.agents.quality.visual_critic import VisualCriticAgent, extract_reference_frame
from showrunner_api.llm_client import clamp_duration, download_file, generate_video_i2v, generate_video_t2v
from showrunner_api.services.series_bible import SeriesBibleService

logger = logging.getLogger(__name__)


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


def _shot_duration(shot: dict[str, Any]) -> int:
    # StoryboardAgent now writes "duration_sec" (already clamped 2-15s), but
    # fall back to the raw LLM field name in case a shot dict reaches this
    # agent from somewhere else that predates that guarantee.
    return clamp_duration(shot.get("duration_sec") if shot.get("duration_sec") is not None else shot.get("estimated_duration_sec"))


class VideoRoutingAgent(BaseAgent):
    """
    Dispatches to video generators based on shot type.
    Includes the Critic-Optimizer loop for character consistency.

    Character-lock handling:
      - `character_refs` (input_json) maps locked character name -> a still
        reference image path (from SeriesBibleService.get_locked_reference_images(),
        wired in by pipeline.py). Any shot whose "characters_in_shot" list
        (set by storyboard.py) intersects this map gets rendered with i2v
        conditioned on that reference instead of plain t2v — this is the
        actual mechanism that stops identity drift; the Visual Critic only
        catches drift after the fact.
      - If a shot names a locked character that has NO reference image yet
        (nothing uploaded, nothing bootstrapped), that character is
        auto-bootstrapped: its first shot is rendered and critiqued
        sequentially (not in the parallel batch), a still is extracted from
        the result, and it's locked in the SeriesBible as lock_source=
        "auto_bootstrap" so every other shot referencing that name — in
        this episode and any later one — renders against a consistent
        anchor instead of each independently hallucinating an appearance.
    """

    async def _render_one(
        self,
        shot: dict[str, Any],
        critic: VisualCriticAgent,
        reference_image_paths: list[str],
        conditioning_image: str | None,
        job_dir: str,
    ) -> dict[str, Any]:
        prompt = shot.get("visual_prompt") or _fallback_visual_prompt(shot)
        duration = _shot_duration(shot)
        max_retries = 3
        attempts = 0
        best_clip = None
        best_score = 0.0
        clip_path = None
        engine = "Wan (Qwen Cloud)"  # default so it's always defined even if the loop body changes later

        while attempts < max_retries:
            attempts += 1
            # 1. Render
            if shot.get("dialogue"):
                # Stub HappyHorse for now if dialogue, Wan doesn't do lip-sync well
                engine = "HappyHorse (Fal.ai)"
                clip_url = f"https://example.com/stub_happyhorse_{uuid.uuid4().hex[:8]}.mp4"
            elif conditioning_image:
                engine = "Wan i2v (Qwen Cloud, character-locked)"
                clip_url = await generate_video_i2v(
                    image_path=conditioning_image,
                    prompt=prompt,
                    duration=duration,
                )
            else:
                engine = "Wan t2v (Qwen Cloud)"
                clip_url = await generate_video_t2v(
                    prompt=prompt,
                    size="720*1280",
                    duration=duration,
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
                reference_image_paths=reference_image_paths,
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
                    "duration_sec": duration,
                    "score": score,
                    "attempts": attempts,
                    "passed": True,
                }

            # Optimizer rewriting
            if verdict["revised_prompt"]:
                prompt = verdict["revised_prompt"]

        # Guarantee a path (falling back to the last attempted clip) and
        # flag the shot as not passed so callers can decide whether to
        # proceed, retry the whole shot, or surface it to the user.
        # assembly.py does Path(clip["clip_path"]) unconditionally and would
        # crash on None.
        return {
            "shot_number": shot.get("shot_number"),
            "engine_used": engine,
            "clip_path": best_clip if best_clip is not None else clip_path,
            "duration_sec": duration,
            "score": best_score,
            "attempts": attempts,
            "passed": False,
        }

    async def run(self, input_json: dict[str, Any]) -> dict[str, Any]:
        # workspace_id is used by BaseAgent.execute() for job tracking; this
        # method itself doesn't need it directly.
        _workspace_id = uuid.UUID(input_json["_workspace_id"])
        project_id = uuid.UUID(input_json["_project_id"]) if "_project_id" in input_json else None

        shots = input_json.get("shots", [])
        if not shots:
            return {"error": "shots list is required"}

        critic = VisualCriticAgent(db=self.db, graph=self.graph, mcp=self.mcp, token_budget=self.token_budget)
        series_bible = SeriesBibleService(db=self.db) if project_id else None

        job_dir = tempfile.mkdtemp(prefix="convertale_job_")

        # character_refs: {name: ref_image_path} for characters already
        # locked with a reference image (user-uploaded or previously
        # bootstrapped). Passed in by pipeline.py from
        # SeriesBibleService.get_locked_reference_images().
        character_refs: dict[str, str] = dict(input_json.get("character_refs") or {})

        def refs_for(shot: dict[str, Any]) -> list[str]:
            names = shot.get("characters_in_shot") or []
            return [character_refs[n] for n in names if n in character_refs]

        def conditioning_for(shot: dict[str, Any]) -> str | None:
            # i2v takes a single conditioning image. If a shot features two
            # locked characters, we still only condition on one (the first
            # in shot order) — genuinely compositing two distinct locked
            # faces into one i2v call isn't something the API supports; the
            # Visual Critic (given both reference stills) is what actually
            # enforces the second character's identity for that shot.
            r = refs_for(shot)
            return r[0] if r else None

        results_by_shot_number: dict[Any, dict[str, Any]] = {}

        # --- Phase 1: sequential bootstrap for any locked-but-unreferenced character ---
        # A character can be "locked" by name (via storyboard's
        # locked_characters) without yet having a reference image, e.g. the
        # user typed a protagonist name but didn't upload a photo. Rendering
        # that character's shots in parallel with no anchor at all is
        # exactly the original drift bug. Instead, render ONE shot for each
        # such character first, sequentially, then lock whatever it produced
        # as an auto-bootstrapped reference before the parallel batch below
        # uses it to condition every other shot with that character.
        if series_bible is not None:
            needs_bootstrap: dict[str, dict[str, Any]] = {}
            for shot in shots:
                for name in shot.get("characters_in_shot") or []:
                    if name not in character_refs and name not in needs_bootstrap:
                        needs_bootstrap[name] = shot

            for name, shot in needs_bootstrap.items():
                sn = shot.get("shot_number")
                logger.info("Bootstrapping reference image for locked character %r via shot %s", name, sn)
                result = await self._render_one(
                    shot, critic, reference_image_paths=[], conditioning_image=None, job_dir=job_dir
                )
                results_by_shot_number[sn] = result
                if result.get("clip_path"):
                    still = await extract_reference_frame(result["clip_path"])
                    if still:
                        await series_bible.lock_character(
                            project_id=project_id, name=name, ref_image_path=still, lock_source="auto_bootstrap"
                        )
                        character_refs[name] = still
                    else:
                        logger.warning("Could not extract a bootstrap still for character %r; leaving unlocked", name)

        # --- Phase 2: parallel render of every shot not already rendered in Phase 1 ---
        remaining_shots = [s for s in shots if s.get("shot_number") not in results_by_shot_number]
        tasks = [
            self._render_one(
                shot,
                critic,
                reference_image_paths=refs_for(shot),
                conditioning_image=conditioning_for(shot),
                job_dir=job_dir,
            )
            for shot in remaining_shots
        ]

        # return_exceptions=True: if one shot's render still fails after its
        # own retries, the other shots that were already accepted by Alibaba
        # keep rendering and their clips get saved, instead of the whole
        # episode's in-flight jobs being abandoned mid-run.
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        for shot, result in zip(remaining_shots, raw_results):
            sn = shot.get("shot_number")
            if isinstance(result, BaseException):
                logger.error("Shot %s failed to render: %s", sn, result)
                results_by_shot_number[sn] = {
                    "shot_number": sn,
                    "engine_used": None,
                    "clip_path": None,
                    "score": 0.0,
                    "attempts": 0,
                    "passed": False,
                    "error": str(result),
                }
            else:
                results_by_shot_number[sn] = result

        generated_clips = [results_by_shot_number[shot.get("shot_number")] for shot in shots]

        failed_shots = [c for c in generated_clips if not c.get("passed", True)]
        if failed_shots:
            shot_numbers = [c.get("shot_number") for c in failed_shots]
            return {
                "clips": generated_clips,
                "status": "completed_with_warnings",
                "job_dir": job_dir,
                "failed_shot_numbers": shot_numbers,
            }

        return {"clips": generated_clips, "status": "completed", "job_dir": job_dir}
