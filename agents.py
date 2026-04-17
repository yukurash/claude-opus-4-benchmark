"""各カテゴリのエージェント定義。

どのエージェントも同じインタフェース:
    run(client, task) -> result dict
を持つ。これにより runner から統一的に呼べる。
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from client import ModelClient


# -------------------------------
# 1. Coding Agent
# -------------------------------
CODING_SYSTEM = """You are an expert Python engineer.
Given a buggy function and failing tests, return the FIXED function only.
Wrap code in a single ```python ... ``` block. No explanation."""


def _extract_code(text: str) -> str:
    m = re.search(r"```python\s*(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else text.strip()


def run_coding(client: ModelClient, task: dict[str, Any]) -> dict[str, Any]:
    user = f"# Buggy function\n{task['buggy_code']}\n\n# Failing tests\n{task['tests']}"
    out = client.complete(CODING_SYSTEM, user)
    code = _extract_code(out["text"])

    # ローカルで単体テスト実行
    passed = False
    err = ""
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "solution.py"
        f.write_text(code + "\n\n" + task["tests"], encoding="utf-8")
        try:
            proc = subprocess.run(
                [sys.executable, str(f)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            passed = proc.returncode == 0
            err = proc.stderr
        except subprocess.TimeoutExpired:
            err = "timeout"

    return {
        **out,
        "extracted_code": code,
        "passed": passed,
        "error": err[:500],
    }


# -------------------------------
# 2. Reasoning Agent
# -------------------------------
REASONING_SYSTEM = """You are a careful reasoner.
Think step by step, then output the final answer on the last line as:
ANSWER: <value>"""


def run_reasoning(client: ModelClient, task: dict[str, Any]) -> dict[str, Any]:
    out = client.complete(REASONING_SYSTEM, task["question"])
    m = re.search(r"ANSWER:\s*(.+)", out["text"])
    answer = m.group(1).strip() if m else ""
    correct = answer.lower().strip(".") == str(task["expected"]).lower().strip(".")
    return {**out, "answer": answer, "expected": task["expected"], "correct": correct}


# -------------------------------
# 3. Long Context Agent (Needle in a Haystack)
# -------------------------------
LONG_CTX_SYSTEM = """You will receive a long document with a hidden fact inside.
Answer ONLY the question using info from the document.
Output format:
ANSWER: <value>"""


def run_long_context(client: ModelClient, task: dict[str, Any]) -> dict[str, Any]:
    haystack = _build_haystack(task["needle"], task["position"], task["target_tokens"])
    user = f"{haystack}\n\nQuestion: {task['question']}"
    out = client.complete(LONG_CTX_SYSTEM, user)
    m = re.search(r"ANSWER:\s*(.+)", out["text"])
    answer = m.group(1).strip() if m else ""
    correct = task["expected"].lower() in answer.lower()
    return {**out, "answer": answer, "correct": correct}


_FILLER = (
    "The quick brown fox jumps over the lazy dog. "
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
)


def _build_haystack(needle: str, position: float, target_tokens: int) -> str:
    # ざっくり 1token≒4chars で近似
    total_chars = target_tokens * 4
    filler_needed = total_chars - len(needle)
    before_len = int(filler_needed * position)
    after_len = filler_needed - before_len
    before = (_FILLER * (before_len // len(_FILLER) + 1))[:before_len]
    after = (_FILLER * (after_len // len(_FILLER) + 1))[:after_len]
    return f"{before}\n\n{needle}\n\n{after}"


# -------------------------------
# 4. Tool Use Agent
# -------------------------------
TOOL_SYSTEM = """You are an autonomous agent. Use the provided tools to accomplish the task.
Break down the goal into tool calls. Stop only when the goal is fully achieved."""

DUMMY_TOOLS = [
    {
        "name": "search_web",
        "description": "Search the web for a query. Returns top 3 snippets.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "calculator",
        "description": "Evaluate a math expression.",
        "input_schema": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    },
    {
        "name": "read_file",
        "description": "Read a local file.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a local file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
]


def run_tool_use(client: ModelClient, task: dict[str, Any]) -> dict[str, Any]:
    out = client.complete(TOOL_SYSTEM, task["goal"], tools=DUMMY_TOOLS)
    called = [c["name"] for c in out["tool_calls"]]
    expected = set(task["required_tools"])
    hit = len(expected.intersection(called))
    return {
        **out,
        "called_tools": called,
        "required_tools": list(expected),
        "coverage": round(hit / len(expected), 2) if expected else 0,
    }


# -------------------------------
# 5. Japanese NLP Agent
# -------------------------------
JA_SYSTEM = """あなたは日本語の専門家です。指示に厳密に従い、出力だけを返してください。"""


def run_ja_nlp(client: ModelClient, task: dict[str, Any]) -> dict[str, Any]:
    out = client.complete(JA_SYSTEM, task["prompt"])
    return {**out, "output": out["text"].strip()}


AGENTS = {
    "coding": run_coding,
    "reasoning": run_reasoning,
    "long_context": run_long_context,
    "tool_use": run_tool_use,
    "ja_nlp": run_ja_nlp,
}
