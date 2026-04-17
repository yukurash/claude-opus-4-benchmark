"""共通設定。"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent
TASKS_DIR = ROOT / "tasks"
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)


@dataclass(frozen=True)
class ModelSpec:
    label: str
    model_id: str


MODEL_A = ModelSpec("Opus 4.6", os.getenv("MODEL_A", "claude-opus-4-6-20260115"))
MODEL_B = ModelSpec("Opus 4.7", os.getenv("MODEL_B", "claude-opus-4-7-20260401"))
JUDGE = ModelSpec("Judge (Opus 4.7)", os.getenv("MODEL_B", "claude-opus-4-7-20260401"))

API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

DEFAULT_TEMPERATURE = 0.0
DEFAULT_MAX_TOKENS = 4096
