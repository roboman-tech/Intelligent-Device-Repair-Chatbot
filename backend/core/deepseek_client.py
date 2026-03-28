import json
import logging
import re
import threading
from typing import Any

import httpx

from backend.core.config import settings

logger = logging.getLogger(__name__)

_JSON_BRACE = re.compile(r"\{[\s\S]*\}")

_httpx_lock = threading.Lock()
_httpx_client: httpx.Client | None = None


def _get_httpx_client() -> httpx.Client:
    global _httpx_client
    if _httpx_client is not None:
        return _httpx_client
    with _httpx_lock:
        if _httpx_client is None:
            _httpx_client = httpx.Client(
                timeout=httpx.Timeout(120.0),
                limits=httpx.Limits(max_keepalive_connections=8, max_connections=16),
            )
    return _httpx_client


def close_deepseek_http_client() -> None:
    """Close pooled connections (call from app shutdown)."""
    global _httpx_client
    with _httpx_lock:
        if _httpx_client is not None:
            _httpx_client.close()
            _httpx_client = None


def _api_unavailable_fallback(
    summary: str,
    extra_steps: list[str] | None = None,
) -> tuple[str, dict[str, Any]]:
    steps = [
        "Check your internet connection and VPN (try turning VPN off or on).",
        "Confirm `DEEPSEEK_BASE_URL` in `.env` is exactly `https://api.deepseek.com/v1` (no typos, no quotes issues).",
        "From PowerShell: `nslookup api.deepseek.com` — if it fails, fix DNS or firewall.",
        "Restart the backend after changing `.env`.",
    ]
    if extra_steps:
        steps = extra_steps + steps
    fb = {
        "issue_summary": summary,
        "needs_followup": True,
        "followup_questions": [
            "What device and symptom can you describe while offline help is limited?",
            "Did this start after a drop, update, or spill?",
        ],
        "likely_causes": [],
        "steps": steps[:8],
        "warnings": [],
        "escalate": False,
    }
    return json.dumps(fb), fb


def chat_completion_json(
    messages: list[dict[str, str]],
    temperature: float = 0.3,
) -> tuple[str, dict[str, Any] | None]:
    """Call DeepSeek chat completions; parse JSON object from assistant message."""
    if not settings.deepseek_api_key:
        fb = _api_unavailable_fallback(
            "Configure DEEPSEEK_API_KEY for full AI replies.",
            extra_steps=[
                "Add your API key to `.env` and restart the backend.",
                "Run `python scripts/ingest_data.py` to build the vector index.",
            ],
        )
        return fb

    url = f"{settings.deepseek_base_url.rstrip('/')}/chat/completions"
    body = {
        "model": settings.deepseek_chat_model,
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {settings.deepseek_api_key}",
        "Content-Type": "application/json",
    }
    try:
        client = _get_httpx_client()
        r = client.post(url, json=body, headers=headers)
        r.raise_for_status()
        data = r.json()
    except httpx.HTTPStatusError as e:
        logger.warning(
            "DeepSeek HTTP error %s: %s",
            e.response.status_code,
            (e.response.text or "")[:300],
        )
        return _api_unavailable_fallback(
            f"The DeepSeek API returned HTTP {e.response.status_code}. Check your API key and account limits.",
            extra_steps=["Open https://api.deepseek.com in a browser only to verify your network allows it."],
        )
    except httpx.RequestError as e:
        # ConnectError / getaddrinfo failed, timeouts, TLS, etc.
        logger.warning("DeepSeek request failed (%s): %s", type(e).__name__, e)
        hint = (
            "Your PC could not reach the API host (DNS error 11001 = hostname not resolved). "
            "Usually: no internet, wrong DEEPSEEK_BASE_URL, corporate firewall, or DNS/VPN issues."
        )
        return _api_unavailable_fallback(hint)

    content = data["choices"][0]["message"]["content"]
    parsed = _extract_json_object(content)
    return content, parsed


def _extract_json_object(text: str) -> dict[str, Any] | None:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = _JSON_BRACE.search(text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    return None
