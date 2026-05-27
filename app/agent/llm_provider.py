from __future__ import annotations

import asyncio
import json
import logging
import re

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Module-level shared HTTP client. Created lazily, disposed by FastAPI lifespan
# and Celery worker shutdown hooks. Reusing it gives us a connection pool
# instead of paying TLS / TCP handshake cost on every LLM call.
_http_client: httpx.AsyncClient | None = None
_http_lock = asyncio.Lock()


async def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None:
        async with _http_lock:
            if _http_client is None:
                _http_client = httpx.AsyncClient(
                    timeout=httpx.Timeout(90.0, connect=10.0),
                    limits=httpx.Limits(
                        max_connections=20, max_keepalive_connections=10
                    ),
                )
    return _http_client


async def close_http_client() -> None:
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


class LLMProvider:
    """LLM client with system prompts, retries, JSON mode and a pooled HTTP client.

    Backward-compatible: `generate(prompt)` is still the single-prompt entry point
    used by the existing agent components and tests.
    """

    def __init__(self, stub: bool = False) -> None:
        self.stub = stub
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.api_url = settings.LLM_API_URL
        self.api_key = settings.LLM_API_KEY
        self.max_retries = 2

    async def generate(self, prompt: str) -> str:
        if self.stub:
            return "stub"
        return await self.chat(system=None, user=prompt, temperature=0.2)

    async def chat(
        self,
        system: str | None,
        user: str,
        temperature: float = 0.3,
        json_mode: bool = False,
        max_tokens: int | None = None,
    ) -> str:
        if self.stub:
            return "stub"

        last_exc: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                if self.provider == "ollama":
                    return await self._call_ollama(
                        system, user, temperature, json_mode, max_tokens
                    )
                if self.provider == "openai":
                    return await self._call_openai(
                        system, user, temperature, json_mode, max_tokens
                    )
                logger.warning("Unknown LLM provider %s", self.provider)
                return ""
            except (httpx.HTTPError, httpx.TimeoutException) as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                raise last_exc
        return ""

    async def _call_ollama(
        self,
        system: str | None,
        user: str,
        temperature: float,
        json_mode: bool,
        max_tokens: int | None,
    ) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user})

        options: dict[str, object] = {"temperature": temperature}
        if max_tokens:
            options["num_predict"] = max_tokens
        payload: dict[str, object] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": options,
        }
        if json_mode:
            payload["format"] = "json"

        url = self.api_url.replace("/api/generate", "/api/chat")
        client = await get_http_client()
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "") or data.get("response", "")

    async def _call_openai(
        self,
        system: str | None,
        user: str,
        temperature: float,
        json_mode: bool,
        max_tokens: int | None,
    ) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user})

        payload: dict[str, object] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        if max_tokens:
            payload["max_tokens"] = max_tokens

        client = await get_http_client()
        resp = await client.post(
            self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


def extract_json(text: str) -> dict[str, object] | None:
    """Robust JSON extraction from LLM output (handles ```json fences, prose)."""
    if not text:
        return None
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    candidate = fenced.group(1) if fenced else None
    if candidate is None:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        candidate = match.group() if match else text
    try:
        result = json.loads(candidate)
        return result if isinstance(result, dict) else None
    except json.JSONDecodeError:
        return None


def detect_language(text: str) -> str:
    """Lightweight RU/EN detector.

    Prefers Russian whenever the text has a meaningful amount of Cyrillic —
    technical tickets often mix in English product names and stack frames, so
    a strict `cyrillic > latin` rule misclassifies them as English.
    """
    if not text:
        return "en"
    cyrillic = len(re.findall(r"[Ѐ-ӿ]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if cyrillic >= 8 or (cyrillic and cyrillic >= 0.25 * (cyrillic + latin)):
        return "ru"
    return "en"
