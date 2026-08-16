# Current Task

> **Note:** Execution notes are session working memory, not a product contract. Lasting facts belong in [current MVP](../reference/current-mvp.md), the [API reference](../reference/api.md), or [CHANGELOG.md](../../CHANGELOG.md).

Align the WikiAI codebase with its core epistemic database vision:

> The modern Wikipedia should not primarily be a website. It should be a public epistemic database — machine-readable, human-verified, with provenance and confidence at the claim level.

## Completed in this session (2026-08-16)

- remediated all 16 findings from the security review: untracked the runtime database, hashed and expired bearer sessions, moved logout to the `Authorization` header, blocked reviewer self-approval and assignment takeover, restricted sign-in redirects, tightened CORS, and added process-local rate limits
- documented the shipped controls and the accepted limitations in `docs/reference/security.md`
- populated `claim_citations.evidence_span` from article section text at seed
- computed claim `confidence` as weakest supporting citation tier; persisted and exposed `confidence_metrics`
- wired contradiction detection on claim insert (`claim_conflict` and `source_conflict`); returned on claim objects
- entity graph now returns outgoing then incoming relationships
- JSON-LD endpoints set `Content-Type: application/ld+json`
- added and updated claim/entity/JSON-LD tests in `apps/api/tests/test_claims_entities.py`

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
