# Review Notes

> **Note:** Execution notes are session working memory, not a product contract. Residual gaps here should match [current MVP](../reference/current-mvp.md).

## Outcome

The repository now contains the WikiAI blueprint and a working MVP scaffold implementing an epistemic database.

This should be classified as:

- `MVP`: yes
- `Production-ready v1`: no

## What Works End-to-End

- seeded article read, search, and article-chat flows
- contributor suggestion and source submission with durable review queue
- reviewer queue with filters, self-assignment, notes, and decision history
- admin audit log, session inspection, and revocation
- atomic claims: each article exposes addressable claims with type, confidence, and citation chain
- knowledge graph: entities with typed outgoing and incoming relationships, linked to articles
- machine-readable export: JSON-LD per article and full `@graph` bulk export with `application/ld+json`
- claim confidence computed from weakest supporting source tier, with `confidence_metrics` on the claim
- evidence spans populated from article section text
- contradiction detection on claim insert, exposed on the claim object

## Residual Gaps

### Epistemic database (highest priority)

- claim extraction is hand-seeded; needs AI pipeline to extract claims from section text automatically

### Security

A security review on 2026-08-16 raised 16 findings. All are remediated; see the changelog and [security](../reference/security.md) for the shipped controls. Verified by 52 passing API tests plus direct probes of session hashing, expiry, and the session cap.

These were accepted rather than fixed. They are documented under [known limitations](../reference/security.md#known-limitations), not open work items:

- rate limits key on the socket address, so a reverse proxy collapses all callers into one bucket
- the limiter evicts its own oldest key once the table passes 10,000 entries
- export paging bounds the response body, not the work the server does to build it
- expired session rows are purged only during login

Blocking for production, in priority order: demo auth, TLS with HSTS, trusted-proxy client IPs plus a shared limiter, and a Content-Security-Policy.

### Infrastructure

- SQLite by default for local dev; switch to PostgreSQL via `WIKIAI_DATABASE_URL`
- no real source ingestion or verification worker runtime
- search is lexical, not OpenSearch-backed
- article chat is grounded to seeded content, not a full RAG pipeline
- demo auth uses seeded accounts, not a production identity system

### UI and workflow

- no optimistic updates or robust inline validation on contributor forms
- no richer audit explorer with pagination or export
- no account lifecycle management beyond session revocation

## Recommended Next Step

- AI claim extraction pipeline: extract atomic claims from article section text automatically
