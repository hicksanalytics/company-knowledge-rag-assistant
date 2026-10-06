from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .embeddings import SentenceTransformerEmbedder
from .ingest import DEFAULT_INDEX


@dataclass(frozen=True)
class SearchResult:
    score: float
    metadata: dict

    @property
    def citation(self) -> str:
        page = f" · page {self.metadata['page']}" if self.metadata.get("page") else ""
        return f"[{self.metadata['source']}{page} · {self.metadata['section']} · passage {self.metadata['passage']}]"


def search(query: str, index_dir: Path = DEFAULT_INDEX, top_k: int = 5, embedder=None) -> list[SearchResult]:
    vectors_path = index_dir / "vectors.npy"
    passages_path = index_dir / "passages.json"
    if not vectors_path.exists() or not passages_path.exists():
        raise FileNotFoundError("Index not found. Run: python -m src.ingest")

    vectors = np.load(vectors_path)
    passages = json.loads(passages_path.read_text(encoding="utf-8"))
    embedder = embedder or SentenceTransformerEmbedder()
    query_vector = embedder.encode([query])[0]
    scores = vectors @ query_vector
    order = np.argsort(-scores)[: min(top_k, len(passages))]
    return [SearchResult(float(scores[i]), passages[int(i)]) for i in order]


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrieve citation-ready company passages.")
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    args = parser.parse_args()
    for rank, result in enumerate(search(args.query, args.index, args.top_k), start=1):
        print(f"\n{rank}. score={result.score:.3f} {result.citation}\n{result.metadata['text']}")


if __name__ == "__main__":
    main()
