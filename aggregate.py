"""結果集計: results/*.json を読んで表とサマリーを吐く。"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.table import Table

from config import MODEL_A, MODEL_B, RESULTS_DIR

console = Console()


def score_row(category: str, rec: dict, label: str) -> dict:
    r = rec[label]
    base = {
        "latency": r["latency_sec"],
        "in_tok": r["usage"]["input_tokens"],
        "out_tok": r["usage"]["output_tokens"],
    }
    if category == "coding":
        base["score"] = 1 if r["passed"] else 0
    elif category == "reasoning":
        base["score"] = 1 if r["correct"] else 0
    elif category == "long_context":
        base["score"] = 1 if r["correct"] else 0
    elif category == "tool_use":
        base["score"] = r["coverage"]
    elif category == "ja_nlp":
        base["score"] = r.get("judge", {}).get("score", 0) / 5.0
    return base


def aggregate() -> pd.DataFrame:
    rows = []
    for f in sorted(RESULTS_DIR.glob("*.json")):
        for rec in json.loads(f.read_text(encoding="utf-8")):
            cat = rec["category"]
            for label in (MODEL_A.label, MODEL_B.label):
                row = {"category": cat, "model": label, "task_id": rec["task_id"]}
                row.update(score_row(cat, rec, label))
                rows.append(row)
    return pd.DataFrame(rows)


def print_summary(df: pd.DataFrame) -> None:
    pivot = df.pivot_table(
        index="category", columns="model", values="score", aggfunc="mean"
    ).round(3)
    latency = df.pivot_table(
        index="category", columns="model", values="latency", aggfunc="mean"
    ).round(2)

    t = Table(title="Score (higher = better)")
    t.add_column("category")
    for c in pivot.columns:
        t.add_column(c)
    for idx, row in pivot.iterrows():
        t.add_row(idx, *[f"{v:.3f}" for v in row])
    console.print(t)

    t2 = Table(title="Avg latency (sec)")
    t2.add_column("category")
    for c in latency.columns:
        t2.add_column(c)
    for idx, row in latency.iterrows():
        t2.add_row(idx, *[f"{v:.2f}" for v in row])
    console.print(t2)


def main() -> None:
    df = aggregate()
    if df.empty:
        console.print("[yellow]no results found. run runner.py first.[/]")
        return
    print_summary(df)
    df.to_csv(RESULTS_DIR / "aggregated.csv", index=False)
    console.print(f"[green]csv:[/] {RESULTS_DIR / 'aggregated.csv'}")


if __name__ == "__main__":
    main()
