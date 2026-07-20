import json
import logging
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any

import asyncio

from showrunner_api.agents.base import BaseAgent
from showrunner_api.llm_client import call_qwen, call_qwen_vision

logger = logging.getLogger(__name__)

_SYSTEM_VL = (
    "You are a film-continuity supervisor judging whether a candidate frame preserves "
    "the identity of one or more locked reference character(s) shown alongside it. Judge by "
    "face, hair, build, and signature features; ignore camera angle, lighting, action, "
    "background, and wardrobe changes between episodes. If two reference characters are "
    "given, the candidate only needs to match whichever of them is actually present in it. "
    "Reply ONLY as JSON: "
    '{"identity": <0.0-1.0>, "same": <true|false>, "reason": "<one sentence>"}.'
)

_REWRITE_SYSTEM = (
    "You are a film director's Optimizer. A shot was rendered but scored below "
    "the consistency threshold. Rewrite the video-generation prompt so the next "
    "render matches the intended shot description and keeps the character, world, "
    "and visual style continuous with the rest of the episode. Reply with ONLY the "
    "rewritten prompt as a single paragraph, no preamble, no quotes, no labels."
)


def _extract_frame_sync(clip_path: str) -> str | None:
    src = Path(clip_path)
    if not src.exists():
        return None
    # FIXED: this used to call subprocess.run(["ffmpeg", ...]) unconditionally.
    # If ffmpeg isn't installed/on PATH, subprocess.run raises FileNotFoundError
    # before a process even starts (Windows: "[WinError 2] The system cannot
    # find the file specified") — that's an unhandled exception, not the
    # `proc.returncode != 0` case below, so it would propagate straight up
    # through evaluate_clip -> _render_with_retry -> VideoRoutingAgent.run()
    # and crash the whole pipeline task, same failure mode fixed in
    # assembly.py. Check first and degrade the same way missing frames
    # already do (return None; evaluate_clip's caller treats that as "failed
    # to extract frames, degrading to pass" rather than a hard failure).
    if shutil.which("ffmpeg") is None:
        logger.error("ffmpeg not found on PATH; cannot extract frame for continuity check")
        return None
    out = Path(tempfile.gettempdir()) / f"critic_frame_{src.stem}_{uuid.uuid4().hex[:6]}.png"
    proc = subprocess.run(
        ["ffmpeg", "-y", "-i", str(src), "-frames:v", "1", str(out)],
        capture_output=True,
    )
    if proc.returncode != 0 or not out.exists():
        logger.error(f"ffmpeg frame extraction failed: {proc.stderr}")
        return None
    return str(out)


async def extract_reference_frame(clip_path: str) -> str | None:
    """Extracts a single still frame from a rendered clip. Public so
    VideoRoutingAgent can pull a frame from the first successfully-rendered
    shot and hand it to SeriesBibleService as an auto-bootstrapped lock when
    the user hasn't uploaded a reference image themselves.

    Runs the blocking ffmpeg call in a worker thread. VideoRoutingAgent
    renders shots concurrently via asyncio.gather(); a synchronous
    subprocess.run() here would serialize that "parallel" rendering on
    the single event loop.
    """
    return await asyncio.to_thread(_extract_frame_sync, clip_path)


# Kept as an internal alias — evaluate_clip below only ever needs to extract
# a frame from the *candidate* clip now (reference identity comes from
# already-still images), but keep the old private name working in case
# anything else in the codebase still imports it directly.
_extract_frame = extract_reference_frame


class VisualCriticAgent(BaseAgent):
    """
    Critic-Optimizer loop.
    Extracts frames, uses Qwen-VL to judge visual continuity.
    If fails, rewrites prompt using Qwen3 text model.
    """

    async def judge_identity(self, ref_frames: list[str], candidate_frame: str) -> dict[str, Any]:
        """Judges whether candidate_frame shows the same character(s) as
        ref_frames (1-2 locked reference stills), in a single Qwen-VL call —
        this is the token-efficiency piece: one VL call per shot regardless
        of whether 1 or 2 characters are locked, instead of one call per
        character."""
        ref_frames = ref_frames[:2]
        if len(ref_frames) == 1:
            lead_in = "First image is the reference character. Second image is a candidate frame."
        else:
            lead_in = (
                "The first two images are reference characters (character A, then character B). "
                "The last image is a candidate frame. Judge whether the candidate frame preserves "
                "the identity of whichever of those reference characters actually appears in it "
                "(a shot may legitimately only feature one of them)."
            )
        raw = await call_qwen_vision(
            system_prompt=_SYSTEM_VL,
            user_prompt=f"{lead_in} Is the character identity preserved?",
            image_paths=[*ref_frames, candidate_frame],
            json_mode=True,
        )
        try:
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if not m:
                raise ValueError("No JSON found")
            data = json.loads(m.group(0))
            return {
                "identity": max(0.0, min(1.0, float(data.get("identity", 0.0)))),
                "same": bool(data.get("same", False)),
                "reason": str(data.get("reason", "")).strip(),
            }
        except Exception as e:
            logger.error(f"VL parse error: {e}")
            return {"identity": 0.0, "same": False, "reason": "parse error"}

    async def _rewrite_prompt(self, description: str, current_prompt: str) -> str | None:
        user_prompt = (
            f"Shot description (intent): {description}\n"
            f"Current prompt that under-performed: {current_prompt}\n"
            "Rewrite the prompt now."
        )
        try:
            revised = await call_qwen(
                system_prompt=_REWRITE_SYSTEM,
                user_prompt=user_prompt,
                model="qwen-max"
            )
            return revised.strip() if revised else None
        except Exception:
            return None

    async def evaluate_clip(
        self,
        description: str,
        prompt: str,
        clip_path: str,
        reference_image_paths: list[str] | None = None,
        threshold: float = 0.6,
    ) -> dict[str, Any]:
        """Scores one clip against 1-2 locked reference character stills
        and optionally proposes a rewritten prompt.

        `reference_image_paths` are already-still images (uploaded by the
        user or auto-bootstrapped from an earlier shot) — not a video to
        extract a frame from, which is why only the candidate clip needs
        frame extraction here.
        """
        reference_image_paths = [p for p in (reference_image_paths or []) if p]
        if not reference_image_paths:
            # No locked character applies to this shot (or none locked yet
            # at all) — nothing to enforce drift against, so this can't be
            # scored as a failure. Logged distinctly from a real pass so an
            # operator scanning logs can tell "nothing to check" apart from
            # "checked and it passed".
            logger.info("No locked reference for this shot — skipping identity check")
            return {
                "score": 1.0,
                "passed": True,
                "reason": "no locked reference character for this shot",
                "revised_prompt": None,
            }

        frame_a = await extract_reference_frame(clip_path)

        if not frame_a:
            return {
                "score": 1.0,
                "passed": True,
                "reason": "failed to extract candidate frame, degrading to pass",
                "revised_prompt": None,
            }

        result = await self.judge_identity(reference_image_paths, frame_a)
        score = result["identity"]
        passed = score >= threshold
        
        if passed:
            return {
                "score": score,
                "passed": True,
                "reason": f"consistency {score:.3f} >= threshold {threshold:.3f}",
                "revised_prompt": None,
            }
            
        revised_prompt = await self._rewrite_prompt(description, prompt)
        return {
            "score": score,
            "passed": False,
            "reason": f"consistency {score:.3f} < threshold {threshold:.3f}",
            "revised_prompt": revised_prompt,
        }

    async def run(self, input_json: dict[str, Any]) -> dict[str, Any]:
        # This agent is meant to be called as a utility by VideoRoutingAgent
        # but satisfies BaseAgent interface.
        pass
