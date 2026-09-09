"""Optional LLM synthesis layer, gated behind ANTHROPIC_API_KEY.

The TF-IDF retrieval in index.py already finds the right policy excerpts
deterministically and for free. This module is purely additive: if a key is
present, it asks the model to turn those excerpts into a short, directly
-cited answer instead of making the user read three retrieved chunks
themselves. If the key is missing, the call fails, or the SDK isn't
installed, callers fall back to showing the raw excerpts — same pattern as
tfscan's `--explain` and azpipegen's `--enhance`.
"""

from __future__ import annotations

import os

from policyrag.chunking import Chunk

DEFAULT_MODEL = "claude-sonnet-4-5"

_SYSTEM_PROMPT = (
    "You are a compliance policy assistant. Answer the user's question using "
    "ONLY the provided policy excerpts. Cite each claim with the excerpt's "
    "citation label in square brackets, e.g. [data-retention-policy.md — "
    "Retention Periods]. If the excerpts don't fully answer the question, say "
    "what's missing rather than guessing. Keep the answer under 150 words."
)


def synthesize(question: str, retrieved: list[tuple[Chunk, float]]) -> str | None:
    """Return a cited answer synthesized from retrieved chunks, or None on any failure."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key or not retrieved:
        return None

    try:
        import anthropic
    except ImportError:
        return None

    excerpts = "\n\n".join(
        f"[{chunk.citation}]\n{chunk.text}" for chunk, _score in retrieved
    )
    model = os.environ.get("POLICYRAG_MODEL", DEFAULT_MODEL)

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=400,
            system=_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Question: {question}\n\nPolicy excerpts:\n\n{excerpts}",
                }
            ],
        )
        text = "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()
        return text or None
    except Exception:
        return None
