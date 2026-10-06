from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass(frozen=True)
class Passage:
    text: str
    source: str
    section: str
    page: int | None
    passage: int

    def to_dict(self) -> dict:
        return asdict(self)


def _windows(text: str, size: int, overlap: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    step = max(1, size - overlap)
    return [" ".join(words[i : i + size]) for i in range(0, len(words), step) if words[i : i + size]]


def chunk_markdown(text: str, source: str, size: int = 180, overlap: int = 35) -> list[Passage]:
    heading = "Document"
    sections: list[tuple[str, str]] = []
    buffer: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if match:
            if buffer:
                sections.append((heading, "\n".join(buffer)))
            heading, buffer = match.group(1), []
        else:
            buffer.append(line)
    if buffer:
        sections.append((heading, "\n".join(buffer)))

    passages: list[Passage] = []
    number = 1
    for section, body in sections:
        for window in _windows(body, size, overlap):
            passages.append(Passage(window, source, section, None, number))
            number += 1
    return passages


def chunk_pdf(path: Path, size: int = 180, overlap: int = 35) -> list[Passage]:
    from pypdf import PdfReader

    passages: list[Passage] = []
    number = 1
    for page_number, page in enumerate(PdfReader(str(path)).pages, start=1):
        for window in _windows(page.extract_text() or "", size, overlap):
            passages.append(Passage(window, path.name, f"Page {page_number}", page_number, number))
            number += 1
    return passages


def load_document(path: Path) -> list[Passage]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return chunk_pdf(path)
    if suffix in {".md", ".txt"}:
        return chunk_markdown(path.read_text(encoding="utf-8"), path.name)
    return []
