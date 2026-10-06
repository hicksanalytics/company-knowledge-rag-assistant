from __future__ import annotations

import json
from pathlib import Path

from .ingest import ROOT
from .retrieve import search


def main() -> None:
    questions = json.loads((ROOT / "data" / "eval_questions.json").read_text(encoding="utf-8"))
    hits = 0
    for item in questions:
        results = search(item["question"], top_k=5)
        found = any(r.metadata["source"] == item["expected_source"] for r in results)
        hits += int(found)
        print(f"{'PASS' if found else 'MISS'} | {item['question']} | expected {item['expected_source']}")
    print(f"\nRecall@5: {hits}/{len(questions)} = {hits / len(questions):.1%}")


if __name__ == "__main__":
    main()
