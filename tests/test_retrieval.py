import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from src.chunk import chunk_markdown
from src.ingest import build_index
from src.retrieve import search


class FakeEmbedder:
    model_name = "keyword-test-embedder"
    vocabulary = ["pto", "vacation", "invoice", "payment", "security", "vendor"]

    def encode(self, texts):
        rows = []
        for text in texts:
            lowered = text.lower()
            row = np.array([lowered.count(word) for word in self.vocabulary], dtype=np.float32)
            norm = np.linalg.norm(row)
            rows.append(row / norm if norm else row)
        return np.vstack(rows)


class ChunkingTests(unittest.TestCase):
    def test_markdown_preserves_section_and_source(self):
        passages = chunk_markdown("# Handbook\n\n## PTO\nEmployees receive PTO.", "handbook.md")
        self.assertEqual(passages[0].source, "handbook.md")
        self.assertEqual(passages[0].section, "PTO")
        self.assertEqual(passages[0].passage, 1)


class RetrievalTests(unittest.TestCase):
    def test_index_and_retrieve_with_citation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            docs, index = root / "docs", root / "index"
            docs.mkdir()
            (docs / "handbook.md").write_text("# PTO\nVacation PTO is available.", encoding="utf-8")
            (docs / "payables.md").write_text("# Invoice\nInvoice payment runs happen weekly.", encoding="utf-8")
            build_index(docs, index, FakeEmbedder())
            result = search("invoice payment", index, 1, FakeEmbedder())[0]
            self.assertEqual(result.metadata["source"], "payables.md")
            self.assertIn("[payables.md", result.citation)
            manifest = json.loads((index / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["documents"], 2)


if __name__ == "__main__":
    unittest.main()
