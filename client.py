"""Anthropic APIクライアントラッパー。"""
from __future__ import annotations

import time
from typing import Any

from anthropic import Anthropic

from config import API_KEY, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE


class ModelClient:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        self._client = Anthropic(api_key=API_KEY)

    def complete(
        self,
        system: str,
        user: str,
        *,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        t0 = time.perf_counter()
        kwargs: dict[str, Any] = {
            "model": self.model_id,
            "system": system,
            "messages": [{"role": "user", "content": user}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools

        resp = self._client.messages.create(**kwargs)
        latency = time.perf_counter() - t0

        text = "".join(
            block.text for block in resp.content if getattr(block, "type", "") == "text"
        )
        tool_calls = [
            {"name": b.name, "input": b.input}
            for b in resp.content
            if getattr(b, "type", "") == "tool_use"
        ]

        return {
            "text": text,
            "tool_calls": tool_calls,
            "latency_sec": round(latency, 3),
            "usage": {
                "input_tokens": resp.usage.input_tokens,
                "output_tokens": resp.usage.output_tokens,
            },
        }
