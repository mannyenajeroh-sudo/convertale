import asyncio
import json
import logging
import os
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Any

from sqlalchemy import select

from showrunner_api.agents.base import BaseAgent
from showrunner_api.models import Episode

logger = logging.getLogger(__name__)

# FIXED: previously the final URL was a stub pointing at https://example.com/...
# which never hosted anything, so the dashboard had no real video to play.
# job_dir lives under tempfile.mkdtemp() (see routing.py), which the OS can
# clean up at any time — so we also copy the finished file out to a
# persistent, servable directory instead of leaving it only in temp.
#
# Requires mounting this directory in main.py, e.g.:
#     from fastapi.staticfiles import StaticFiles
#     from showrunner_api.agents.production.assembly import MEDIA_DIR
#     app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
MEDIA_DIR = Path(os.getenv("MEDIA_DIR", "media")).resolve()
MEDIA_DIR.mkdir(parents=True, exist_ok=True)
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000").rstrip("/")

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


def _persist_to_media_sync(src_path: str, output_name: str) -> Path:
    dest = MEDIA_DIR / output_name
    shutil.copy2(src_path, dest)
    return dest


# Logo overlay tuning: small, corner-anchored, slightly transparent so it
# reads as a channel bug / brand watermark rather than covering the shot.
# 12% of frame width scales sensibly across different logo aspect ratios;
# 85% opacity and a soft drop shadow keep it visible over both light and
# dark backgrounds without looking pasted-on.
_LOGO_WIDTH_FRACTION = 0.16
_LOGO_MARGIN_PX = 28
_LOGO_OPACITY = 0.85


class AssemblyAgent(BaseAgent):
    """
    Concatenates clips, burns subtitles, and (if a brand logo is set for the
    project) composites it as a corner watermark to create the final
    assembled episode MP4. Updates the Episode record in the DB with the
    final URL.
    """

    async def run(self, input_json: dict[str, Any]) -> dict[str, Any]:
        # workspace_id / project_id are used by BaseAgent.execute() for job
        # tracking; this method itself doesn't need them directly.
        _workspace_id = uuid.UUID(input_json["_workspace_id"])
        _project_id = uuid.UUID(input_json["_project_id"]) if "_project_id" in input_json else None

        episode_id_str = input_json.get("episode_id")
        clips = input_json.get("clips", [])
        job_dir = input_json.get("job_dir")
        # Optional: path to the project's uploaded brand logo (see
        # routers/brand_assets.py + Project.brand_logo_path). None/missing
        # file both degrade gracefully to "no watermark" rather than failing
        # the whole episode's assembly.
        logo_path = input_json.get("logo_path")

        if not episode_id_str or not clips or not job_dir:
            return {"error": "episode_id, clips, and job_dir are required"}

        episode_id = uuid.UUID(episode_id_str)
        job_path = Path(job_dir)

        # FIXED: previously a missing ffmpeg/ffprobe install surfaced as a raw
        # FileNotFoundError ("[WinError 2] The system cannot find the file
        # specified" on Windows) from deep inside asyncio.to_thread(subprocess.run),
        # which propagated up through execute() and killed the whole background
        # pipeline task with an unhandled-exception traceback. Check up front and
        # return a normal {"error": ...} result instead, so pipeline.py's existing
        # `if "error" in assembly_result` handling can log it cleanly and move on
        # to the next episode instead of the whole run aborting.
        missing = [exe for exe in ("ffmpeg", "ffprobe") if shutil.which(exe) is None]
        if missing:
            return {
                "error": (
                    f"{' and '.join(missing)} not found on PATH. Install ffmpeg "
                    "(which bundles ffprobe) and ensure its bin/ directory is on "
                    "this machine's PATH, then restart the API server so the new "
                    "PATH is picked up."
                )
            }

        logo_file = Path(logo_path).resolve() if logo_path else None
        use_logo = bool(logo_file and logo_file.exists())
        if logo_path and not use_logo:
            logger.warning(f"logo_path set ({logo_path}) but file not found on disk; skipping watermark")

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

        # 3. burn subtitles + (optionally) composite the logo watermark, in a
        # single ffmpeg pass. Combining both into one filter_complex avoids a
        # second full re-encode of the episode just to add a watermark.
        output_name = f"episode_{episode_id.hex[:8]}.mp4"
        subtitles_filter = f"subtitles=subs.srt:force_style='{_SUB_STYLE}'"

        if use_logo:
            cmd = [
                "ffmpeg", "-y",
                "-i", "concat.mp4",
                "-i", str(logo_file),
                "-filter_complex",
                (
                    f"[1:v]scale=iw*{_LOGO_WIDTH_FRACTION}:-1,format=rgba,"
                    f"colorchannelmixer=aa={_LOGO_OPACITY}[wm];"
                    f"[0:v][wm]overlay=W-w-{_LOGO_MARGIN_PX}:H-h-{_LOGO_MARGIN_PX}:format=auto[ov];"
                    f"[ov]{subtitles_filter}[outv]"
                ),
                "-map", "[outv]",
                "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
                output_name,
            ]
        else:
            cmd = [
                "ffmpeg", "-y", "-i", "concat.mp4", "-vf", subtitles_filter,
                "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
                output_name
            ]

        try:
            await asyncio.to_thread(
                subprocess.run, cmd, check=True, capture_output=True, cwd=str(job_path),
            )
        except subprocess.CalledProcessError as exc:
            if use_logo:
                # Don't let a bad/corrupt logo file (wrong format, 0 bytes,
                # unsupported codec) take down the whole episode — retry once
                # without the watermark rather than failing assembly outright.
                logger.error(
                    "Logo overlay pass failed (%s); retrying without watermark: %s",
                    logo_file, exc.stderr,
                )
                fallback_cmd = [
                    "ffmpeg", "-y", "-i", "concat.mp4", "-vf", subtitles_filter,
                    "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
                    output_name
                ]
                await asyncio.to_thread(
                    subprocess.run, fallback_cmd, check=True, capture_output=True, cwd=str(job_path),
                )
            else:
                raise

        rendered_path = str(job_path / output_name)

        # FIXED: copy out of the (possibly ephemeral) job_dir into a durable,
        # servable media directory, and build a real URL the browser can
        # actually reach — instead of the previous stub example.com URL.
        persisted_path = await asyncio.to_thread(_persist_to_media_sync, rendered_path, output_name)
        final_video_path = str(persisted_path)
        final_video_url = f"{BACKEND_BASE_URL}/media/{output_name}"

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
