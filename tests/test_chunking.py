from pathlib import Path

from policyrag.chunking import chunk_directory, chunk_document

REPO_ROOT = Path(__file__).parent.parent
POLICIES_DIR = REPO_ROOT / "policies"


def test_chunk_document_splits_by_heading():
    chunks = chunk_document(POLICIES_DIR / "data-retention-policy.md")
    headings = {c.heading for c in chunks}
    assert "Retention Periods" in headings
    assert "Disposal Process" in headings
    assert all(c.title == "Data Retention Policy" for c in chunks)


def test_chunk_citation_format():
    chunks = chunk_document(POLICIES_DIR / "access-control-policy.md")
    first = chunks[0]
    assert first.source_file == "access-control-policy.md"
    assert first.heading in first.citation
    assert first.source_file in first.citation


def test_chunk_directory_covers_all_shipped_policies():
    chunks = chunk_directory(POLICIES_DIR)
    files = {c.source_file for c in chunks}
    assert files == {
        "access-control-policy.md",
        "data-retention-policy.md",
        "gdpr-data-processing-policy.md",
        "incident-response-policy.md",
        "third-party-risk-policy.md",
    }


def test_long_section_is_split_with_overlap(tmp_path):
    body = "This sentence repeats. " * 120  # well over MAX_CHUNK_CHARS
    doc = tmp_path / "long.md"
    doc.write_text(f"# Long Doc\n\n## Big Section\n\n{body}\n")

    chunks = chunk_document(doc)
    assert len(chunks) > 1
    assert all(c.heading == "Big Section" for c in chunks)
    # chunk_index should be sequential starting at 0
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))


def test_document_without_headings_falls_back_to_title_chunk(tmp_path):
    doc = tmp_path / "flat.md"
    doc.write_text("# Flat Doc\n\nJust one paragraph, no ## sections at all.\n")

    chunks = chunk_document(doc)
    assert len(chunks) == 1
    assert chunks[0].heading == "Flat Doc"
