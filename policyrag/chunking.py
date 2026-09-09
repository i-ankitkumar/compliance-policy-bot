"""Splits policy markdown documents into retrievable chunks.

Chunking is heading-aware: each `##` section becomes a chunk so a retrieved
result is always a coherent, citable unit ("Data Retention Policy > Retention
Periods") rather than an arbitrary slice of text. A section that's still too
long to be a useful single chunk is further split into overlapping windows so
no single chunk is so large it drowns out a specific match.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

MAX_CHUNK_CHARS = 900
OVERLAP_CHARS = 150

_HEADING_RE = re.compile(r"^##\s+(.*)$", re.MULTILINE)


@dataclass
class Chunk:
    source_file: str
    title: str
    heading: str
    chunk_index: int
    text: str

    @property
    def citation(self) -> str:
        suffix = f" (part {self.chunk_index + 1})" if self.chunk_index else ""
        return f"{self.source_file} — {self.heading}{suffix}"


def _split_long_section(text: str) -> list[str]:
    text = text.strip()
    if len(text) <= MAX_CHUNK_CHARS:
        return [text] if text else []

    windows = []
    start = 0
    while start < len(text):
        end = min(start + MAX_CHUNK_CHARS, len(text))
        # Prefer to break on a sentence/paragraph boundary near the end.
        if end < len(text):
            boundary = text.rfind("\n\n", start, end)
            if boundary == -1:
                boundary = text.rfind(". ", start, end)
            if boundary != -1 and boundary > start + 100:
                end = boundary + 1
        windows.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - OVERLAP_CHARS, start + 1)
    return [w for w in windows if w]


def chunk_document(path: str | Path) -> list[Chunk]:
    """Parse one markdown policy document into a list of Chunks."""
    path = Path(path)
    raw = path.read_text(encoding="utf-8")

    title_match = re.match(r"^#\s+(.*)$", raw, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.stem

    headings = list(_HEADING_RE.finditer(raw))
    chunks: list[Chunk] = []

    if not headings:
        for i, window in enumerate(_split_long_section(raw)):
            chunks.append(Chunk(path.name, title, title, i, window))
        return chunks

    for idx, match in enumerate(headings):
        heading = match.group(1).strip()
        body_start = match.end()
        body_end = headings[idx + 1].start() if idx + 1 < len(headings) else len(raw)
        body = raw[body_start:body_end]
        for i, window in enumerate(_split_long_section(body)):
            chunks.append(Chunk(path.name, title, heading, i, window))

    return chunks


def chunk_directory(directory: str | Path) -> list[Chunk]:
    """Chunk every *.md file directly under `directory`."""
    directory = Path(directory)
    chunks: list[Chunk] = []
    for path in sorted(directory.glob("*.md")):
        chunks.extend(chunk_document(path))
    return chunks
