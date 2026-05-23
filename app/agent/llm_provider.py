import httpx

from app.config import settings


class LLMProvider:
    def __init__(self, stub: bool = False) -> None:
        self.stub = stub
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.api_url = settings.LLM_API_URL
        self.api_key = settings.LLM_API_KEY

    async def generate(self, prompt: str) -> str:
        if self.stub:
            return "stub"

        if self.provider == "ollama":
            return await self._call_ollama(prompt)
        elif self.provider == "openai":
            return await self._call_openai(prompt)
        return ""

    async def _call_ollama(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                self.api_url,
                json={"model": self.model, "prompt": prompt, "stream": False},
            )
            resp.raise_for_status()
            return resp.json().get("response", "")

    async def _call_openai(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]
