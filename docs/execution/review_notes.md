# Review Notes

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
- knowledge graph: entities with typed relationships, linked to articles
- machine-readable export: JSON-LD per article and full `@graph` bulk export

## Residual Gaps

### Epistemic database (highest priority)

- claim extraction is hand-seeded; needs AI pipeline to extract claims from section text automatically
- `evidence_span` in `claim_citations` is empty; should store exact quoted passage from source document
- claim-level confidence is hand-set; needs computation from source quality, cross-source agreement, freshness, and human review
- `contradictions` table exists in SQL schema but is not wired to claims layer
- `confidence_metrics` table exists in SQL schema but is not computed or exposed via API
- entity graph only returns outgoing relationships; incoming traversal missing
- no `application/ld+json` content-type header on JSON-LD endpoints

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

- wire contradiction detection: when a new claim is added, check for conflicts with existing claims on the same article
- implement confidence computation: aggregate source quality + cross-source agreement + human review score into `confidence_metrics`
- populate `evidence_span`: when a claim is created, extract the supporting quote from the linked source document
- add test coverage for claim and entity endpoints
