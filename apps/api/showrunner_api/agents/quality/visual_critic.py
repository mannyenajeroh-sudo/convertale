import json
import logging
import re
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
    "You are a film-continuity supervisor judging whether two video frames show "
    "the SAME recurring character. Judge by face, hair, build, and signature "
    "features; ignore camera angle, lighting, action, background, and wardrobe "
    "changes between episodes. Reply ONLY as JSON: "
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
    out = Path(tempfile.gettempdir()) / f"critic_frame_{src.stem}_{uuid.uuid4().hex[:6]}.png"
    proc = subprocess.run(
        ["ffmpeg", "-y", "-i", str(src), "-frames:v", "1", str(out)],
        capture_output=True,
    )
    if proc.returncode != 0 or not out.exists():
        logger.error(f"ffmpeg frame extraction failed: {proc.stderr}")
        return None
    return str(out)


async def _extract_frame(clip_path: str) -> str | None:
    # Runs the blocking ffmpeg call in a worker thread. VideoRoutingAgent
    # renders shots concurrently via asyncio.gather(); a synchronous
    # subprocess.run() here would serialize that "parallel" rendering on
    # the single event loop.
    return await asyncio.to_thread(_extract_frame_sync, clip_path)


class VisualCriticAgent(BaseAgent):
    """
    Critic-Optimizer loop.
    Extracts frames, uses Qwen-VL to judge visual continuity.
    If fails, rewrites prompt using Qwen3 text model.
    """

    async def judge_identity(self, ref_frame: str, candidate_frame: str) -> dict[str, Any]:
        raw = await call_qwen_vision(
            system_prompt=_SYSTEM_VL,
            user_prompt="First image is the reference character. Second image is a candidate frame. Is it the same character?",
            image_paths=[ref_frame, candidate_frame],
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
        self, description: str, prompt: str, clip_path: str, reference_clip_path: str | None = None, threshold: float = 0.6
    ) -> dict[str, Any]:
        """Scores one clip and optionally proposes a rewritten prompt."""
        if not reference_clip_path:
            return {
                "score": 1.0,
                "passed": True,
                "reason": "no reference clip",
                "revised_prompt": None,
            }
            
        frame_a = await _extract_frame(clip_path)
        frame_b = await _extract_frame(reference_clip_path)
        
        if not frame_a or not frame_b:
            return {
                "score": 1.0,
                "passed": True,
                "reason": "failed to extract frames, degrading to pass",
                "revised_prompt": None,
            }
            
        result = await self.judge_identity(frame_b, frame_a)
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
