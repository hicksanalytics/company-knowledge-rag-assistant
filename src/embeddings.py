from __future__ import annotations

import json
from urllib.request import Request, urlopen

import numpy as np

DEFAULT_MODEL = "nomic-embed-text"
DEFAULT_ENDPOINT = "http://127.0.0.1:11434/api/embed"


class SentenceTransformerEmbedder:
    """
    Creates embeddings through the local Ollama API.

    The original class name is retained so the rest of the project
    does not need to change.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        endpoint: str = DEFAULT_ENDPOINT,
    ):
        self.model_name = model_name
        self.endpoint = endpoint

    def encode(self, texts: list[str]) -> np.ndarray:
        payload = json.dumps(
            {
                "model": self.model_name,
                "input": texts,
            }
        ).encode("utf-8")

        request = Request(
            self.endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise RuntimeError(
                "Could not reach the local Ollama embedding service. "
                "Confirm Ollama is running and nomic-embed-text is installed."
            ) from exc

        vectors = np.asarray(result["embeddings"], dtype=np.float32)
        return normalize(vectors)


def normalize(vectors: np.ndarray) -> np.ndarray:
    vectors = np.asarray(vectors, dtype=np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.maximum(norms, 1e-12)