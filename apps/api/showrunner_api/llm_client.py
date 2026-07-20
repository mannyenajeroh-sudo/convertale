import base64
import logging
import time
import uuid
from pathlib import Path
from typing import Any

import dashscope
import httpx
from dashscope import VideoSynthesis

from showrunner_api.config import get_settings

logger = logging.getLogger(__name__)

# Get settings with cache cleared to ensure fresh load on module reload
settings = get_settings(clear_cache=True)

# Initialize dashscope SDK (if API key is present)
if settings.effective_dashscope_key:
    dashscope.api_key = settings.effective_dashscope_key
    logger.info(f"Dashscope initialized with key prefix: {settings.effective_dashscope_key[:8]}...")
else:
    logger.warning("No QWEN_API_KEY or DASHSCOPE_API_KEY configured - API calls will return stub responses")

# Video duration constraints
MIN_VIDEO_DURATION_SEC = 3
MAX_VIDEO_DURATION_SEC = 10

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
    Call Qwen text API using httpx with OpenAI-compatible endpoint.
    """
    api_key = settings.effective_dashscope_key
    if not api_key:
        logger.warning("QWEN_API_KEY / DASHSCOPE_API_KEY is not set. Returning stub response.")
        if json_mode:
            return "{}"
        return "Stub response since no Qwen API key is configured."

    # Ensure base URL doesn't have trailing slash before appending path
    base_url = settings.qwen_base_url.rstrip("/")
    url = f"{base_url}/chat/completions"
    
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
        
    # Log request details (without exposing full key)
    key_preview = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) >= 12 else api_key[:8]
    logger.debug(f"Calling Qwen API: POST {url} with key {key_preview}, model={model}")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            
            # Log response status for debugging
            if response.status_code != 200:
                logger.error(
                    f"Qwen API returned {response.status_code}: {response.text[:200]}"
                )
                
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            logger.debug(f"Qwen API response received ({len(content)} chars)")
            return content
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling Qwen API: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error calling Qwen API: {e}")
            raise


def _image_uri(path: str | Path) -> str:
    data = Path(path).read_bytes()
    return "data:image/png;base64," + base64.b64encode(data).decode()


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
        
    # We use synchronous Dashscope SDK for submission, wrapped or just directly if it's quick
    # (Dashscope SDK does network request so it blocks, but we can live with it for this submission step)
    task = VideoSynthesis.call(
        model=model,
        prompt=prompt,
        size=size,
        duration=duration,
    )
    if task.status_code != 200:
        raise RuntimeError(f"Wan submit failed: {task.status_code} {task.code} {task.message}")
        
    return await _poll_task(task.output.task_id, poll_interval=poll_interval, timeout=timeout)


async def _poll_task(task_id: str, poll_interval: int = 8, timeout: int = 600) -> str:
    """Poll /tasks/{id} tolerating transient network errors."""
    url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
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
