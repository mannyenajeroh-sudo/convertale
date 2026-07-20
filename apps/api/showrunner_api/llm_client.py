import asyncio
import base64
import logging
import time
import uuid
from pathlib import Path
from typing import Any

import dashscope
import httpx
from dashscope import VideoSynthesis
from dashscope.common.error import InvalidTask

from showrunner_api.config import get_settings

logger = logging.getLogger(__name__)

# FIXED: the free-tier wan2.6-t2v endpoint throttles task *creation*
# (429 Throttling.RateQuota), not just total account usage. Firing all of
# an episode's shots at once via VideoRoutingAgent's asyncio.gather()
# reliably tripped this. Alibaba still *accepts and runs* whichever
# submissions land under the limit, so a naive "just raise" here burns
# real quota on jobs the app then abandons the moment the first 429
# propagates. A small submission-side semaphore plus retry/backoff fixes
# both the throttling itself and the quota waste it was causing.
_SUBMIT_SEMAPHORE = asyncio.Semaphore(2)  # max concurrent task *submissions* to Dashscope
_SUBMIT_MAX_RETRIES = 5
_SUBMIT_BASE_BACKOFF = 8  # seconds; doubles each retry

settings = get_settings()

# Initialize dashscope SDK (if API key is present)
if settings.effective_dashscope_key:
    dashscope.api_key = settings.effective_dashscope_key

    # FIXED: VideoSynthesis (and any other call that goes through the native
    # DashScope SDK protocol, as opposed to the OpenAI-compatible httpx calls
    # below) reads its endpoint from dashscope.base_http_api_url — a
    # SEPARATE config value from settings.qwen_base_url. We were only ever
    # setting dashscope.api_key, so the SDK fell back to its default
    # endpoint, which does not recognize a workspace-scoped key (sk-ws-...)
    # at all. This is documented behavior: Alibaba's own text-to-video API
    # reference for wan2.6-t2v/ap-southeast-1 requires explicitly setting
    # dashscope.base_http_api_url = 'https://{WorkspaceId}.ap-southeast-1
    # .maas.aliyuncs.com/api/v1' for exactly this key type. Derive it from
    # the same host already proven correct by the successful text/vision
    # calls (settings.qwen_base_url), swapping the OpenAI-compatible path
    # suffix for the SDK's native "/api/v1" path — rather than hardcoding a
    # second, independent copy of the workspace host that could drift out
    # of sync with qwen_base_url.
    _workspace_host = settings.qwen_base_url.split("://", 1)[-1].split("/", 1)[0]
    dashscope.base_http_api_url = f"https://{_workspace_host}/api/v1"
    logger.info(f"✓ Dashscope SDK base_http_api_url set to {dashscope.base_http_api_url}")

_TRANSIENT_EXCEPTIONS = (
    httpx.ConnectError,
    httpx.TimeoutException,
    httpx.ReadError,
    httpx.ProxyError,
)

async def call_qwen(
    system_prompt: str,
    user_prompt: str,
    model: str = "qwen-max",
    temperature: float = 0.7,
    json_mode: bool = False,
) -> str:
    """
    Call Qwen text API using httpx.
    """
    api_key = settings.effective_dashscope_key
    if not api_key:
        logger.warning("QWEN_API_KEY / DASHSCOPE_API_KEY is not set. Returning stub response.")
        if json_mode:
            return "{}"
        return "Stub response since no Qwen API key is configured."

    url = f"{settings.qwen_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    logger.info(f"🤖 Calling Qwen API: model={model}, json_mode={json_mode}")
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            start = time.monotonic()
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            logger.info(f"✓ Qwen API response received in {time.monotonic() - start:.2f}s")
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling Qwen API: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error calling Qwen API: {e}")
            raise


_MIME_BY_EXT = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def _image_uri(path: str | Path) -> str:
    p = Path(path)
    mime = _MIME_BY_EXT.get(p.suffix.lower(), "image/png")
    data = p.read_bytes()
    return f"data:{mime};base64," + base64.b64encode(data).decode()


async def call_qwen_vision(
    system_prompt: str,
    user_prompt: str,
    image_paths: list[str | Path],
    model: str = "qwen-vl-plus",
    temperature: float = 0.7,
    json_mode: bool = False,
) -> str:
    """
    Call Qwen-VL multimodal API. Images are sent as base64 data URIs.
    """
    api_key = settings.effective_dashscope_key
    if not api_key:
        logger.warning("QWEN_API_KEY / DASHSCOPE_API_KEY is not set. Returning stub response.")
        if json_mode:
            return '{"identity": 1.0, "same": true, "reason": "stub"}'
        return "Stub vision response."

    url = f"{settings.qwen_base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    content: list[dict[str, Any]] = [{"type": "text", "text": user_prompt}]
    for p in image_paths:
        content.append({"type": "image_url", "image_url": {"url": _image_uri(p)}})

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ]

    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def _submit_video_task_with_retry(*, model: str, call_kwargs: dict[str, Any]) -> Any:
    """Shared submit/backoff logic for both t2v and i2v: caps concurrent
    submissions via _SUBMIT_SEMAPHORE and retries a 429 with exponential
    backoff instead of raising immediately (see module docstring above for
    why this matters for quota). Runs the blocking VideoSynthesis.call() in
    a worker thread so the event loop stays free (see generate_video_t2v's
    original FIXED note — applies identically here).

    Extracted out of generate_video_t2v so generate_video_i2v doesn't
    duplicate this loop verbatim.
    """
    task = None
    async with _SUBMIT_SEMAPHORE:
        for attempt in range(1, _SUBMIT_MAX_RETRIES + 1):
            try:
                task = await asyncio.to_thread(VideoSynthesis.call, model=model, **call_kwargs)
                break
            except InvalidTask as exc:
                # 429 shows up here, not as a status_code check below, because
                # dashscope's own .call()->.wait() raises InvalidTask before
                # ever returning a response object when task creation itself
                # was rejected.
                if "429" not in str(exc) and "RateQuota" not in str(exc):
                    raise
                if attempt == _SUBMIT_MAX_RETRIES:
                    logger.error(f"✗ Giving up on video submission after {attempt} rate-limited attempts")
                    raise
                wait_s = _SUBMIT_BASE_BACKOFF * (2 ** (attempt - 1))
                logger.warning(
                    f"⏳ Rate-limited submitting video task (attempt {attempt}/{_SUBMIT_MAX_RETRIES}); "
                    f"backing off {wait_s}s before retry"
                )
                await asyncio.sleep(wait_s)

    if task.status_code != 200:
        raise RuntimeError(f"Wan submit failed: {task.status_code} {task.code} {task.message}")
    return task


async def _resolve_video_url(task: Any, poll_interval: int, timeout: int) -> str:
    # VideoSynthesis.call() already blocks internally until the task reaches
    # a terminal state (see dashscope's base_api.py: .call() invokes .wait()
    # for you), so task.output should already carry the finished video_url
    # here rather than needing a fresh round of polling from scratch.
    video_url = getattr(task.output, "video_url", None)
    if video_url:
        return video_url

    # Fallback: if the SDK ever returns before the task is actually terminal
    # (e.g. a future SDK version splitting submit/wait behavior), poll it
    # ourselves via raw HTTP.
    return await _poll_task(task.output.task_id, poll_interval=poll_interval, timeout=timeout)


# wan2.6-t2v / wan2.6-i2v-flash both accept an integer duration from 2-15
# seconds (default 5), billed per second — confirmed against Alibaba Model
# Studio's current API reference. Clamp to that range everywhere a caller
# supplies a duration so an LLM-estimated or user-edited value can never
# reach the API out of bounds.
MIN_VIDEO_DURATION_SEC = 2
MAX_VIDEO_DURATION_SEC = 15


def clamp_duration(duration: float | int | None, default: int = 5) -> int:
    if duration is None:
        return default
    try:
        d = round(float(duration))
    except (TypeError, ValueError):
        return default
    return max(MIN_VIDEO_DURATION_SEC, min(MAX_VIDEO_DURATION_SEC, d))


async def generate_video_t2v(
    prompt: str,
    size: str = "720*1280",
    duration: int = 5,
    model: str = "wan2.6-t2v",
    poll_interval: int = 8,
    timeout: int = 600,
) -> str:
    """
    Submit a Wan text-to-video task via Dashscope SDK and poll raw HTTP until done.
    Returns the MP4 URL.
    """
    if not settings.effective_dashscope_key:
        logger.warning("No QWEN_API_KEY, returning stub video URL.")
        return f"https://example.com/stub_{uuid.uuid4().hex[:8]}.mp4"

    duration = clamp_duration(duration)
    logger.info(f"🎬 Submitting T2V task: model={model}, duration={duration}s")

    task = await _submit_video_task_with_retry(
        model=model,
        call_kwargs={"prompt": prompt, "size": size, "duration": duration},
    )
    return await _resolve_video_url(task, poll_interval, timeout)


async def generate_video_i2v(
    image_path: str | Path,
    prompt: str = "",
    duration: int = 5,
    model: str = "wan2.6-i2v-flash",
    resolution: str = "720P",
    audio: bool = False,
    poll_interval: int = 8,
    timeout: int = 600,
) -> str:
    """
    Submit a Wan image-to-video task, conditioned on a local reference still
    (base64-encoded — no public hosting needed). This is the actual
    character-consistency mechanism: unlike t2v, i2v anchors the generated
    video to the pixels of a specific reference image instead of re-deriving
    the character from text alone each time, which is what let identity
    drift shot-to-shot in the first place.

    Note: i2v derives output aspect ratio from the input image itself, not
    from a `size` param (that's why there's no `size` arg here) — callers
    must ensure the reference still is already 9:16 portrait to match the
    episode format (720x1280).
    """
    if not settings.effective_dashscope_key:
        logger.warning("No QWEN_API_KEY, returning stub video URL.")
        return f"https://example.com/stub_{uuid.uuid4().hex[:8]}.mp4"

    duration = clamp_duration(duration)
    logger.info(f"🎬 Submitting I2V task: model={model}, duration={duration}s, ref={image_path}")

    img_uri = _image_uri(image_path)
    call_kwargs: dict[str, Any] = {
        "img_url": img_uri,
        "duration": duration,
        "resolution": resolution,
        "audio": audio,
    }
    if prompt:
        call_kwargs["prompt"] = prompt

    task = await _submit_video_task_with_retry(model=model, call_kwargs=call_kwargs)
    return await _resolve_video_url(task, poll_interval, timeout)


async def _poll_task(task_id: str, poll_interval: int = 8, timeout: int = 600) -> str:
    """Poll /tasks/{id} tolerating transient network errors."""
    # FIXED: was hardcoded to the generic https://dashscope.aliyuncs.com
    # host. A workspace-scoped key (sk-ws-...) is only valid against its own
    # workspace endpoint — same root cause as the base_http_api_url fix
    # above. Reuse the same derived workspace host so task-status polling
    # doesn't 401 the same way task submission did.
    workspace_host = settings.qwen_base_url.split("://", 1)[-1].split("/", 1)[0]
    url = f"https://{workspace_host}/api/v1/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {settings.effective_dashscope_key}"}
    deadline = time.time() + timeout
    transient = 0

    async with httpx.AsyncClient() as client:
        while time.time() < deadline:
            try:
                resp = await client.get(url, headers=headers, timeout=30.0)
                resp.raise_for_status()
                out = resp.json().get("output", {})
                status = out.get("task_status")

                if status == "SUCCEEDED":
                    return out["video_url"]
                if status == "FAILED":
                    raise RuntimeError(f"Wan task {task_id} FAILED: {out}")

                transient = 0
            except _TRANSIENT_EXCEPTIONS as exc:
                transient += 1
                if transient > 8:
                    raise RuntimeError(f"Wan poll {task_id}: too many transient errors: {exc}")

            # Simple async sleep
            import asyncio
            await asyncio.sleep(poll_interval)

    raise TimeoutError(f"Wan task {task_id} not finished within {timeout}s")


async def download_file(url: str, dest: str | Path, retries: int = 4) -> Path:
    """Download a remote file to dest asynchronously."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    last_err = None

    import asyncio
    async with httpx.AsyncClient() as client:
        for attempt in range(retries):
            try:
                async with client.stream("GET", url, timeout=180.0) as r:
                    r.raise_for_status()
                    with open(dest, "wb") as f:
                        async for chunk in r.aiter_bytes(chunk_size=65536):
                            f.write(chunk)
                return dest
            except _TRANSIENT_EXCEPTIONS as exc:
                last_err = exc
                await asyncio.sleep(2 * (attempt + 1))

    raise RuntimeError(f"download failed after {retries} attempts: {last_err}")
