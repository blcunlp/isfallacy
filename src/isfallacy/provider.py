"""OpenAI-compatible text generation client with bounded retries."""

from __future__ import annotations

import os

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential_jitter


class OpenAICompatibleProvider:
    def __init__(self, model: str, base_url: str | None = None, api_key: str | None = None):
        self.model = model
        resolved_key = api_key or os.getenv("OPENAI_API_KEY")
        if not resolved_key:
            raise ValueError("Set OPENAI_API_KEY or pass --api-key.")
        self.client = OpenAI(
            api_key=resolved_key,
            base_url=base_url or os.getenv("OPENAI_BASE_URL") or None,
        )

    @retry(
        wait=wait_exponential_jitter(initial=1, max=30), stop=stop_after_attempt(6), reraise=True
    )
    def generate(self, prompt: str, temperature: float = 0.0, max_tokens: int = 512) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return (response.choices[0].message.content or "").strip()
