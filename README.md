# policyrag — RAG Compliance Policy Bot

A small retrieval-augmented Q&A bot for internal policy documents (data
retention, access control, incident response, vendor risk, GDPR/DSGVO). Ask
a question in plain English, get back the exact policy excerpts that answer
it, each with a precise citation — no vector database, no embedding API, no
cost, and nothing to configure.

## Why

Most "policy chatbot" demos reach for an embedding model and a vector
database on day one, which is the wrong place to start for a corpus of a few
dozen governance documents: it adds a paid API dependency, a moving part
that can silently drift out of sync with the source files, and a retrieval
step whose scoring is opaque. This project starts from the other end —
term-frequency retrieval is exact, deterministic, and fully explainable
(`explain()` shows precisely which words matched), and it's genuinely
sufficient for policy corpora, where questions and answers share vocabulary
almost by definition ("retention period" questions match documents that say
"retention period"). An LLM only gets involved, optionally, to turn the
retrieved excerpts into a readable, still-cited answer.

## How it works

```
policies/*.md  ──chunk_directory()──▶  heading-aware Chunks  ──TfidfIndex.from_chunks()──▶  TF-IDF vectors
                                                                        │
                                                          query ──▶ index.search() ──▶ ranked (Chunk, score)
                                                                        │
                                                          ┌─────────────┴─────────────┐
                                                          │                           │
                                                 always: print excerpts     --synthesize: answer.synthesize()
                                                 with citation + score      (Claude API, optional, graceful
                                                                             fallback to excerpts-only)
```

Each `##` heading in a policy document becomes one retrievable, citable
chunk (`data-retention-policy.md — Retention Periods`); a section too long
to be a useful single chunk is split into overlapping windows so no chunk
is so large it drowns out a specific match. Retrieval is cosine similarity
over TF-IDF vectors built with nothing but the standard library.

## Install

```bash
pip install -e .
# optional: pip install -e ".[ai]"   # to enable --synthesize
```

## Usage

```bash
$ policyrag ask "how long do we retain financial and billing records" --top-k 2
```

```
                                     Top 2 matching excerpt(s)
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Score ┃ Source                                     ┃ Excerpt                                     ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 0.222 │ data-retention-policy.md — Retention       │ Customer account data is retained for the   │
│       │ Periods                                    │ duration of the active contract             │
│       │                                            │ plus 90 days after termination, to support  │
│       │                                            │ account recovery requests.                  │
│       │                                            │ Financial and billing records are retained  │
│       │                                            │ for 7 years to satisfy tax and              │
│       │                                            │ audit requirements. Application and         │
│       │                                            │ infrastructure logs (including access       │
│       │                                            │ logs and audit trails) ar...                │
├───────┼────────────────────────────────────────────┼─────────────────────────────────────────────┤
│ 0.113 │ data-retention-policy.md — Scope           │ Applies to all data processed or stored by  │
│       │                                            │ the organization, including                 │
│       │                                            │ customer data, employee records, system     │
│       │                                            │ logs, and backups, across all               │
│       │                                            │ environments (production, staging, and      │
│       │                                            │ development).                               │
└───────┴────────────────────────────────────────────┴─────────────────────────────────────────────┘
```

A question whose answer spans two policies retrieves from both, correctly
ranked:

```bash
$ policyrag ask "what is the deadline to notify the regulator after a breach" --top-k 2
```

```
                                     Top 2 matching excerpt(s)
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Score ┃ Source                                      ┃ Excerpt                                    ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 0.219 │ gdpr-data-processing-policy.md — Breach     │ A personal data breach is handled under    │
│       │ Notification                                │ the Incident Response Policy, which        │
│       │                                             │ governs the 72-hour supervisory authority  │
│       │                                             │ notification deadline and data             │
│       │                                             │ subject notification for high-risk         │
│       │                                             │ breaches.                                  │
├───────┼─────────────────────────────────────────────┼────────────────────────────────────────────┤
│ 0.197 │ incident-response-policy.md — Regulatory    │ Where an incident constitutes a personal   │
│       │ Notification                                │ data breach under applicable data          │
│       │                                             │ protection law (including GDPR Article     │
│       │                                             │ 33), the Data Protection Officer must      │
│       │                                             │ be notified within 4 hours of              │
│       │                                             │ confirmation, so that any required         │
│       │                                             │ regulator                                  │
│       │                                             │ notification can be made within the        │
│       │                                             │ 72-hour statutory window. Affected data    │
│       │                                             │ subjects are n...                          │
└───────┴─────────────────────────────────────────────┴────────────────────────────────────────────┘
```

Pass `--synthesize` (with `ANTHROPIC_API_KEY` set) to turn those excerpts
into a short, still-cited prose answer instead of reading the table
yourself; without a key it prints the excerpts only, with a note that
synthesis was skipped — same fail-soft pattern as the `--enhance` flag in
[azpipegen](https://github.com/i-ankitkumar/azure-pipeline-generator).

`policyrag list` shows what's indexed:

```
                        Indexed policy documents
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ File                           ┃ Title                       ┃ Chunks ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ access-control-policy.md       │ Access Control Policy       │      7 │
│ data-retention-policy.md       │ Data Retention Policy       │      6 │
│ gdpr-data-processing-policy.md │ GDPR Data Processing Policy │      7 │
│ incident-response-policy.md    │ Incident Response Policy    │      7 │
│ third-party-risk-policy.md     │ Third-Party Risk Policy     │      6 │
└────────────────────────────────┴─────────────────────────────┴────────┘
```

Point `--policies-dir` at your own corpus to use this against real internal
policies instead of the sample ones shipped here.

## The sample corpus

Five policy documents covering the governance areas most compliance
programs standardize first: data retention, access control, incident
response, third-party/vendor risk, and GDPR/DSGVO data processing. They're
realistic in structure and cross-reference each other (the GDPR policy
points to the Incident Response policy for breach handling, which in turn
points back to the Data Retention policy for legal-hold handling) so
retrieval has to actually distinguish between related-but-different
sections — not just match on a single unique keyword.

## Development

```bash
pip install -e ".[dev]"
pytest
```

11 tests cover heading-based chunking, long-section splitting with overlap,
TF-IDF tokenization, and retrieval correctness (that a retention question
ranks the retention policy first, that a breach-notification question
surfaces both GDPR and incident-response chunks, that scores sort
descending, and that a query with no vocabulary overlap returns nothing
rather than a spurious guess).

## Roadmap

- [ ] `--synthesize-only` mode that prints just the cited answer, not the excerpt table
- [ ] Optional local embedding backend (sentence-transformers) as a drop-in alternative index for larger corpora
- [ ] A minimal web UI (FastAPI + a single HTML page) for non-CLI users
- [ ] Support for `.txt` and `.pdf` policy sources alongside markdown

## About

Built by [Ankit Kumar](https://iankitkumar.in) — DevOps/Cloud engineer whose
day job includes a Global Policy & Compliance Standards project (governance,
policy enforcement, and compliance frameworks), which is exactly the kind of
"what does our policy actually say about X" question this project answers.
Part of a series of small, real infra/compliance tools — see [pinned
repos](https://github.com/i-ankitkumar) for the others, including
[tfscan](https://github.com/i-ankitkumar/terraform-security-scanner) (policy
enforcement for Terraform) and
[azpipegen](https://github.com/i-ankitkumar/azure-pipeline-generator).

## License

MIT
