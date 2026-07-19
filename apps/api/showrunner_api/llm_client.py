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

# Clear cache to get fresh settings
from showrunner_api.config import clear_settings_cache
clear_settings_cache()
settings = get_settings()

# Initialize dashscope SDK (if API key is present)
if settings.effective_dashscope_key:
    dashscope.api_key = settings.effective_dashscope_key

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
    logger.debug(f"   System prompt length: {len(system_prompt)} chars")
    logger.debug(f"   User prompt length: {len(user_prompt)} chars")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            start_time = time.time()
            response = await client.post(url, headers=headers, json=payload)
            elapsed = time.time() - start_time
            
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            logger.info(f"✓ Qwen API response received in {elapsed:.2f}s")
            logger.debug(f"   Response length: {len(content)} chars")
            
            return content
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HTTP error calling Qwen API: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.TimeoutException as e:
            logger.error(f"⏱️ Timeout calling Qwen API after 120s: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error calling Qwen API: {type(e).__name__}: {e}")
            raise


def _image_uri(path: str | Path) -> str:
    """Convert an image file to a base64 data URI."""
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
    
    logger.info(f"👁️ Calling Qwen-VL API: model={model}, images={len(image_paths)}")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            start_time = time.time()
            response = await client.post(url, headers=headers, json=payload)
            elapsed = time.time() - start_time
            
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            logger.info(f"✓ Qwen-VL API response received in {elapsed:.2f}s")
            return content
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HTTP error calling Qwen-VL API: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.TimeoutException as e:
            logger.error(f"⏱️ Timeout calling Qwen-VL API after 120s: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error calling Qwen-VL API: {type(e).__name__}: {e}")
            raise


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
    
    logger.info(f"🎬 Submitting video generation task: model={model}, duration={duration}s")
        
    # We use synchronous Dashscope SDK for submission
    task = VideoSynthesis.call(
        model=model,
        prompt=prompt,
        size=size,
        duration=duration,
    )
    if task.status_code != 200:
        logger.error(f"❌ Video submission failed: {task.status_code} {task.code} {task.message}")
        raise RuntimeError(f"Wan submit failed: {task.status_code} {task.code} {task.message}")
    
    logger.info(f"✓ Video task submitted successfully, polling for completion...")
        
    return await _poll_task(task.output.task_id, poll_interval=poll_interval, timeout=timeout)


async def _poll_task(task_id: str, poll_interval: int = 8, timeout: int = 600) -> str:
    """Poll /tasks/{id} tolerating transient network errors."""
    url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {settings.effective_dashscope_key}"}
    deadline = time.time() + timeout
    transient = 0
    
    logger.debug(f"Starting poll for task {task_id}, timeout={timeout}s")
    
    async with httpx.AsyncClient() as client:
        while time.time() < deadline:
            try:
                resp = await client.get(url, headers=headers, timeout=30.0)
                resp.raise_for_status()
                out = resp.json().get("output", {})
                status = out.get("task_status")
                
                if status == "SUCCEEDED":
                    logger.info(f"✓ Video task {task_id} completed successfully")
                    return out["video_url"]
                if status == "FAILED":
                    logger.error(f"❌ Video task {task_id} failed: {out}")
                    raise RuntimeError(f"Wan task {task_id} FAILED: {out}")
                    
                transient = 0
                logger.debug(f"Task {task_id} status: {status}, continuing to poll...")
            except _TRANSIENT_EXCEPTIONS as exc:
                transient += 1
                if transient > 8:
                    logger.error(f"❌ Too many transient errors polling task {task_id}: {exc}")
                    raise RuntimeError(f"Wan poll {task_id}: too many transient errors: {exc}")
                logger.warning(f"Transient error polling task {task_id}, retrying... ({transient}/8)")
            
            # Simple async sleep
            import asyncio
            await asyncio.sleep(poll_interval)
            
    logger.error(f"⏱️ Video task {task_id} timed out after {timeout}s")
    raise TimeoutError(f"Wan task {task_id} not finished within {timeout}s")


async def download_file(url: str, dest: str | Path, retries: int = 4) -> Path:
    """Download a remote file to dest asynchronously."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    last_err = None
    
    logger.info(f"⬇️ Downloading file from {url} to {dest}")
    
    import asyncio
    async with httpx.AsyncClient() as client:
        for attempt in range(retries):
            try:
                async with client.stream("GET", url, timeout=180.0) as r:
                    r.raise_for_status()
                    with open(dest, "wb") as f:
                        async for chunk in r.aiter_bytes(chunk_size=65536):
                            f.write(chunk)
                    logger.info(f"✓ File downloaded successfully to {dest}")
                    return dest
            except _TRANSIENT_EXCEPTIONS as exc:
                last_err = exc
                logger.warning(f"Download attempt {attempt+1}/{retries} failed: {exc}, retrying...")
                await asyncio.sleep(2 * (attempt + 1))
                
    logger.error(f"❌ Download failed after {retries} attempts")
    raise RuntimeError(f"download failed after {retries} attempts: {last_err}")