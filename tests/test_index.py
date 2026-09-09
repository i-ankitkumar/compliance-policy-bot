from pathlib import Path

from policyrag.chunking import chunk_directory
from policyrag.index import TfidfIndex, tokenize

REPO_ROOT = Path(__file__).parent.parent
POLICIES_DIR = REPO_ROOT / "policies"


def _index():
    chunks = chunk_directory(POLICIES_DIR)
    return TfidfIndex.from_chunks(chunks), chunks


def test_tokenize_lowercases_and_drops_stopwords():
    tokens = tokenize("The Data Retention Policy is for all customer data.")
    assert "the" not in tokens
    assert "for" not in tokens
    assert "data" in tokens
    assert "retention" in tokens


def test_retrieval_surfaces_the_right_document_top_result():
    index, _chunks = _index()

    results = index.search("how long do we keep financial billing records", top_k=3)
    assert results, "expected at least one match"
    top_chunk, top_score = results[0]
    assert top_chunk.source_file == "data-retention-policy.md"
    assert top_score > 0


def test_retrieval_for_breach_notification_hits_gdpr_or_incident_policy():
    index, _chunks = _index()

    results = index.search("72 hour breach notification to the regulator", top_k=3)
    top_sources = {chunk.source_file for chunk, _score in results}
    assert top_sources & {"gdpr-data-processing-policy.md", "incident-response-policy.md"}


def test_search_results_are_sorted_descending_by_score():
    index, _chunks = _index()
    results = index.search("vendor security questionnaire due diligence", top_k=5)
    scores = [score for _chunk, score in results]
    assert scores == sorted(scores, reverse=True)


def test_search_with_no_overlapping_terms_returns_empty():
    index, _chunks = _index()
    results = index.search("xyzzy quux plugh", top_k=3)
    assert results == []


def test_explain_returns_overlapping_terms():
    index, chunks = _index()
    results = index.search("access review quarterly", top_k=1)
    assert results
    top_chunk, _score = results[0]
    overlap = index.explain("access review quarterly", top_chunk)
    assert "access" in overlap or "review" in overlap or "quarterly" in overlap
