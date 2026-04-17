"""LLM-as-Judge。日本語NLPなどの定性タスクをスコアリング。"""
from __future__ import annotations

import json
import re
from typing import Any

from client import ModelClient
from config import JUDGE

JUDGE_SYSTEM = """You are a strict evaluator. Given a task and a model output,
score the output on a 1-5 scale:
  5 = excellent, natural, fully satisfies the task
  4 = good, minor issues
  3 = acceptable, noticeable issues
  2 = poor, significant issues
  1 = failure

Return ONLY a JSON object:
{"score": <int>, "reason": "<one sentence>"}"""


def judge(task_prompt: str, output: str) -> dict[str, Any]:
    client = ModelClient(JUDGE.model_id)
    user = f"# Task\n{task_prompt}\n\n# Model Output\n{output}"
    out = client.complete(JUDGE_SYSTEM, user, max_tokens=256)
    m = re.search(r"\{.*\}", out["text"], re.DOTALL)
    if not m:
        return {"score": 0, "reason": "parse_error", "raw": out["text"]}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"score": 0, "reason": "parse_error", "raw": out["text"]}
