# Current Task

Align the WikiAI codebase with its core epistemic database vision:

> The modern Wikipedia should not primarily be a website. It should be a public epistemic database — machine-readable, human-verified, with provenance and confidence at the claim level.

## Completed in this session (2026-06-13)

- implemented atomic `claims` layer: each claim is a first-class addressable object with `claim_type`, `status`, `confidence`, and citation chain
- implemented `claim_citations`: links each claim to specific source IDs with `evidence_span` and `support_type`
- implemented knowledge graph: `entities` with typed relationships (`entity_relationships`) and article linkage (`article_entities`)
- added machine-readable API endpoints: `GET /api/v1/articles/{slug}/claims`, `GET /api/v1/claims/{id}`, `GET /api/v1/entities`, `GET /api/v1/entities/{slug}`
- added JSON-LD export: `GET /api/v1/articles/{slug}/jsonld` and `GET /api/v1/export?format=jsonld`
- seeded 6 atomic claims (3 per article), 8 entities, 6 typed relationships
- updated FastAPI app description, `product.md`, and `architecture.md` to position the database as the product
- extended `001_init.sql` with `claim_citations`, `entities`, `entity_relationships`, `article_entities` tables

## Remaining gaps toward full epistemic database

- claim extraction pipeline: currently hand-seeded; should be AI-extracted from section text
- evidence spans: `evidence_span` in `claim_citations` is empty; should reference exact quote from source
- claim-level confidence computation: currently hand-set; should derive from source quality, cross-source agreement, and human review scores
- incoming entity relationships: `GET /api/v1/entities/{slug}` only returns outgoing edges; incoming traversal missing
- `application/ld+json` content-type header on JSON-LD endpoints
- contradiction detection: `contradictions` table in SQL schema, not yet wired to claims layer
- confidence metrics aggregation: `confidence_metrics` table in SQL schema, not yet computed or exposed
- test suite coverage for new claim and entity endpoints
