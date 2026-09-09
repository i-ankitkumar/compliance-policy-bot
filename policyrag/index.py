"""A dependency-free TF-IDF index for retrieving policy chunks.

No embedding model, no vector database, no API key — just term frequencies
and cosine similarity from the standard library. For a corpus of a few dozen
policy documents this retrieves as well as it needs to, it's instant, it's
free, and it's fully inspectable (`explain()` shows exactly which shared
terms drove a match). That's the "rules decide what" half of this project;
`answer.py` is the optional layer that improves *how* the result reads.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field

from policyrag.chunking import Chunk

_TOKEN_RE = re.compile(r"[a-z]{2,}")

_STOPWORDS = {
    "the", "and", "for", "are", "but", "not", "you", "all", "any", "can",
    "had", "her", "was", "one", "our", "out", "day", "get", "has", "him",
    "his", "how", "man", "new", "now", "old", "see", "two", "way", "who",
    "boy", "did", "its", "let", "put", "say", "she", "too", "use", "with",
    "this", "that", "from", "have", "will", "your", "which", "their",
    "shall", "must", "into", "such", "than", "then", "when", "where",
    "should", "would", "each", "these", "those", "been", "being", "also",
    "may", "per", "within", "under", "over", "upon", "onto", "does",
}


def tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS]


@dataclass
class TfidfIndex:
    chunks: list[Chunk]
    idf: dict[str, float] = field(default_factory=dict)
    doc_vectors: list[dict[str, float]] = field(default_factory=list)

    @classmethod
    def from_chunks(cls, chunks: list[Chunk]) -> "TfidfIndex":
        index = cls(chunks=chunks)
        doc_tokens = [tokenize(c.text) for c in chunks]
        n_docs = len(chunks)

        doc_freq: Counter[str] = Counter()
        for tokens in doc_tokens:
            doc_freq.update(set(tokens))

        index.idf = {
            term: math.log((n_docs + 1) / (df + 1)) + 1.0
            for term, df in doc_freq.items()
        }

        for tokens in doc_tokens:
            index.doc_vectors.append(index._vectorize(tokens))

        return index

    def _vectorize(self, tokens: list[str]) -> dict[str, float]:
        counts = Counter(tokens)
        vec = {
            term: count * self.idf.get(term, 0.0)
            for term, count in counts.items()
            if term in self.idf
        }
        norm = math.sqrt(sum(w * w for w in vec.values())) or 1.0
        return {term: w / norm for term, w in vec.items()}

    @staticmethod
    def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
        shorter, longer = (a, b) if len(a) < len(b) else (b, a)
        return sum(w * longer.get(term, 0.0) for term, w in shorter.items())

    def search(self, query: str, top_k: int = 3) -> list[tuple[Chunk, float]]:
        query_vec = self._vectorize(tokenize(query))
        scored = [
            (chunk, self._cosine(query_vec, doc_vec))
            for chunk, doc_vec in zip(self.chunks, self.doc_vectors)
        ]
        scored = [pair for pair in scored if pair[1] > 0]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]

    def explain(self, query: str, chunk: Chunk) -> list[str]:
        """Return the query terms that overlap with `chunk`'s vocabulary, for transparency."""
        query_terms = set(tokenize(query))
        chunk_index = self.chunks.index(chunk)
        chunk_terms = set(self.doc_vectors[chunk_index])
        return sorted(query_terms & chunk_terms)
