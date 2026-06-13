# API Rules

## General

- Public APIs must return evidence and trust metadata for any AI-generated answer.
- Article read APIs must expose `confidence_score`, `last_verified_at`, and revision identifiers.
- Search APIs must separate direct answers from supporting articles and sources.
- Mutation APIs must produce audit log events.
- Review and moderation APIs must enforce RBAC and actor attribution.
- AI-facing APIs must reject ungrounded answer publication.
- Prefer explicit versioning once external clients are introduced.

## Claim endpoints

- `GET /api/v1/articles/{slug}/claims` must return all active claims for the article, each with `confidence`, `claim_type`, `section_key`, and a non-empty `citations` array.
- `GET /api/v1/claims/{id}` must return the full claim object including citation chain with `source_id`, `evidence_span`, and `support_type`.
- Claims with `status: disputed` must be included in responses but flagged; callers must not suppress them.
- Confidence scores on claims must reflect the weakest supporting citation tier, not an average.

## Entity and knowledge graph endpoints

- `GET /api/v1/entities/{slug}` must return typed relationships with `predicate`, `object_slug`, `object_name`, and `confidence`.
- Relationship `confidence` must degrade if the `source_claim_id` it references becomes disputed or deprecated.
- Entity slugs must be stable and human-readable; do not use UUIDs as public identifiers.

## Machine-readable export

- `GET /api/v1/export?format=jsonld` must return a valid JSON-LD `@graph` with `@context: https://schema.org`.
- JSON-LD article nodes must include `citation` arrays referencing source objects with `publisher`, `url`, `datePublished`, and `evidenceTier`.
- Export endpoint is public read; no auth required.
- Future: JSON-LD endpoints should set `Content-Type: application/ld+json`.
