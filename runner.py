"""ベンチマーク実行エントリポイント。

使い方:
    python runner.py --all
    python runner.py --category coding
"""
from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.progress import Progress

from agents import AGENTS
from client import ModelClient
from config import MODEL_A, MODEL_B, RESULTS_DIR, TASKS_DIR
from judge import judge

console = Console()


def load_tasks(category: str) -> list[dict]:
    path = TASKS_DIR / f"{category}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def run_pair(category: str, task: dict) -> dict:
    agent = AGENTS[category]
    client_a = ModelClient(MODEL_A.model_id)
    client_b = ModelClient(MODEL_B.model_id)

    with ThreadPoolExecutor(max_workers=2) as ex:
        fut_a = ex.submit(agent, client_a, task)
        fut_b = ex.submit(agent, client_b, task)
        res_a = fut_a.result()
        res_b = fut_b.result()

    record = {
        "task_id": task["id"],
        "category": category,
        MODEL_A.label: res_a,
        MODEL_B.label: res_b,
    }

    # 定性タスクはJudgeにかける
    if category == "ja_nlp":
        record[MODEL_A.label]["judge"] = judge(task["prompt"], res_a["output"])
        record[MODEL_B.label]["judge"] = judge(task["prompt"], res_b["output"])

    return record


def run_category(category: str) -> list[dict]:
    tasks = load_tasks(category)
    results: list[dict] = []
    with Progress() as progress:
        bar = progress.add_task(f"[cyan]{category}", total=len(tasks))
        for task in tasks:
            results.append(run_pair(category, task))
            progress.advance(bar)
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", choices=list(AGENTS))
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    cats = list(AGENTS) if args.all else [args.category]
    if not cats or cats == [None]:
        parser.error("--all か --category を指定してください")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    for cat in cats:
        console.rule(f"[bold]{cat}")
        results = run_category(cat)
        out = RESULTS_DIR / f"{cat}_{ts}.json"
        out.write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        console.print(f"[green]saved:[/] {out}")


if __name__ == "__main__":
    main()
