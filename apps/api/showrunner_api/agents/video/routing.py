import asyncio
import uuid
import os
import tempfile
from typing import Any

from showrunner_api.agents.base import BaseAgent
from showrunner_api.agents.quality.visual_critic import VisualCriticAgent
from showrunner_api.llm_client import generate_video_t2v, download_file


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
        prompt = shot.get("prompt", "")
        max_retries = 3
        attempts = 0
        best_clip = None
        best_score = 0.0
        
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
            if score > best_score:
                best_score = score
                best_clip = clip_path
                
            if verdict["passed"]:
                return {
                    "shot_number": shot.get("shot_number"),
                    "engine_used": engine,
                    "clip_path": clip_path,
                    "score": score,
                    "attempts": attempts,
                }
                
            # Optimizer rewriting
            if verdict["revised_prompt"]:
                prompt = verdict["revised_prompt"]
                
        return {
            "shot_number": shot.get("shot_number"),
            "engine_used": engine,
            "clip_path": best_clip,
            "score": best_score,
            "attempts": attempts,
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
            
        return {"clips": generated_clips, "status": "completed", "job_dir": job_dir}
