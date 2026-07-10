"""LLM client — thin wrapper over an OpenAI-compatible API (OpenRouter).

Keeps the Senate model-agnostic: any provider exposing /chat/completions works.
Tracks cumulative cost so deliberations respect the constitutional budget
(CONSTITUTION.md Article II §6 — Economy).
"""
from __future__ import annotations

import json
import os
import urllib.request
from typing import Protocol


class ChatClient(Protocol):
    """Anything that can play the role of an LLM in a deliberation."""

    spent_usd: float

    def chat(self, model: str, system: str, user: str, max_tokens: int = 1200) -> str:
        ...


class BudgetExceeded(RuntimeError):
    """Raised when a deliberation would exceed its budget."""


class LLMClient:
    def __init__(self, base_url: str, api_key_env: str, max_usd: float = 0.50):
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ.get(api_key_env, "")
        if not self.api_key:
            raise RuntimeError(f"Missing API key: set {api_key_env}")
        self.max_usd = max_usd
        self.spent_usd = 0.0

    def chat(self, model: str, system: str, user: str, max_tokens: int = 1200) -> str:
        if self.spent_usd >= self.max_usd:
            raise BudgetExceeded(
                f"Deliberation budget exhausted (${self.spent_usd:.4f} >= ${self.max_usd})"
            )
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "usage": {"include": True},
        }
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
        usage = data.get("usage", {})
        # OpenRouter returns cost directly; fall back to 0 for other providers.
        self.spent_usd += float(usage.get("cost", 0.0) or 0.0)
        return data["choices"][0]["message"]["content"]
