from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .chunk import load_document
from .embeddings import DEFAULT_MODEL, SentenceTransformerEmbedder

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCS = ROOT / "data" / "company_docs"
DEFAULT_INDEX = ROOT / "data" / "index"


def build_index(docs_dir: Path, index_dir: Path, embedder=None) -> int:
    paths = sorted(p for p in docs_dir.rglob("*") if p.suffix.lower() in {".md", ".txt", ".pdf"})
    passages = [passage for path in paths for passage in load_document(path)]
    if not passages:
        raise ValueError(f"No supported documents found in {docs_dir}")

    embedder = embedder or SentenceTransformerEmbedder()
    vectors = embedder.encode([p.text for p in passages])
    index_dir.mkdir(parents=True, exist_ok=True)
    np.save(index_dir / "vectors.npy", vectors)
    (index_dir / "passages.json").write_text(
        json.dumps([p.to_dict() for p in passages], indent=2), encoding="utf-8"
    )
    (index_dir / "manifest.json").write_text(
        json.dumps({"model": getattr(embedder, "model_name", "test-embedder"), "documents": len(paths), "passages": len(passages)}, indent=2),
        encoding="utf-8",
    )
    return len(passages)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the local document retrieval index.")
    parser.add_argument("--docs", type=Path, default=DEFAULT_DOCS)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    args = parser.parse_args()
    count = build_index(args.docs, args.index)
    print(f"Indexed {count} passages in {args.index}")
    print(f"Embedding model: {DEFAULT_MODEL}")


if __name__ == "__main__":
    main()
