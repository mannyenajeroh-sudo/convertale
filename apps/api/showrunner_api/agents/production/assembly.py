import asyncio
import json
import logging
import subprocess
import uuid
from pathlib import Path
from typing import Any

from sqlalchemy import select

from showrunner_api.agents.base import BaseAgent
from showrunner_api.models import Episode

logger = logging.getLogger(__name__)

_SUB_STYLE = (
    "FontSize=14,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,"
    "BorderStyle=1,Outline=1,Shadow=0,MarginV=60,Alignment=2"
)


def _duration_sync(path: str) -> float:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
            capture_output=True,
            text=True,
            check=True
        )
        return float(json.loads(out.stdout)["format"]["duration"])
    except Exception as e:
        logger.warning(f"Failed to get duration for {path}: {e}")
        return 5.0  # default


async def _duration(path: str) -> float:
    # Runs the blocking ffprobe call off the event loop. Previously this
    # ran synchronously inside an async agent method, and because
    # VideoRoutingAgent renders shots in parallel via asyncio.gather(),
    # every blocking subprocess.run() call here would serialize what was
    # supposed to be concurrent work on the single event loop.
    return await asyncio.to_thread(_duration_sync, path)


def _srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _write_srt(shots: list[dict], durations: list[float], srt_path: Path) -> None:
    offset = 0.0
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, shot in enumerate(shots):
            dur = durations[i] if i < len(durations) else 5.0
            dialogue = shot.get("dialogue") or shot.get("subtitle", "")
            f.write(f"{i + 1}\n{_srt_time(offset)} --> {_srt_time(offset + dur)}\n")
            f.write(f"{dialogue}\n\n")
            offset += dur


class AssemblyAgent(BaseAgent):
    """
    Concatenates clips and burns subtitles to create the final assembled episode MP4.
    Updates the Episode record in the DB with the final URL.
    """

    async def run(self, input_json: dict[str, Any]) -> dict[str, Any]:
        # workspace_id / project_id are used by BaseAgent.execute() for job
        # tracking; this method itself doesn't need them directly.
        _workspace_id = uuid.UUID(input_json["_workspace_id"])
        _project_id = uuid.UUID(input_json["_project_id"]) if "_project_id" in input_json else None
        
        episode_id_str = input_json.get("episode_id")
        clips = input_json.get("clips", [])
        job_dir = input_json.get("job_dir")
        
        if not episode_id_str or not clips or not job_dir:
            return {"error": "episode_id, clips, and job_dir are required"}
            
        episode_id = uuid.UUID(episode_id_str)
        job_path = Path(job_dir)
        
        # 1. concat list
        concat_list_path = job_path / "concat_list.txt"
        with open(concat_list_path, "w") as f:
            for clip in clips:
                # clip should contain clip_path
                p = Path(clip["clip_path"]).resolve()
                f.write(f"file '{p}'\n")
                
        await asyncio.to_thread(
            subprocess.run,
            [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", "concat_list.txt", "-c", "copy", "concat.mp4"
            ],
            check=True,
            capture_output=True,
            cwd=str(job_path),
        )
        
        # 2. subs
        durations = [await _duration(c["clip_path"]) for c in clips]
        srt_path = job_path / "subs.srt"
        _write_srt(clips, durations, srt_path)
        
        # 3. burn
        output_name = f"episode_{episode_id.hex[:8]}.mp4"
        await asyncio.to_thread(
            subprocess.run,
            [
                "ffmpeg", "-y", "-i", "concat.mp4", "-vf",
                f"subtitles=subs.srt:force_style='{_SUB_STYLE}'",
                "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
                output_name
            ],
            check=True,
            capture_output=True,
            cwd=str(job_path),
        )
        
        final_video_path = str(job_path / output_name)
        
        # In a real app, upload final_video_path to OSS and get public URL
        final_video_url = f"https://example.com/assets/{output_name}"
        
        # Update episode status
        result = await self.db.execute(select(Episode).where(Episode.id == episode_id))
        episode = result.scalars().first()
        if episode:
            episode.status = "completed"
            episode.assembled_video_url = final_video_url
            await self.db.commit()
            
        return {
            "status": "completed",
            "assembled_video_path": final_video_path,
            "assembled_video_url": final_video_url
        }
