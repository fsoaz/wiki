# Current MVP

This page is the canonical narrative for **what the running code does**. The FastAPI source and generated OpenAPI schema are the behavior contract if they disagree with this page. Target design lives in [architecture](../explanation/architecture.md). Do not treat that document as a description of this build.

## Applications

- `apps/web`: Next.js 15 App Router UI for home, article read, search, sign-in, contributor, reviewer, and admin surfaces.
- `apps/api`: FastAPI 0.1.0 service. SQLite by default. Optional PostgreSQL via `WIKIAI_DATABASE_URL`.
- `infra/sql/001_init.sql`: Postgres bootstrap schema for Compose.
- `docker-compose.yml`: local Postgres 17 only. No Redis, OpenSearch, or Kubernetes in this repo.

## Seeded content

On API startup, empty databases receive:

- Demo users: `contributor@example.com`, `reviewer@example.com`, `admin@example.com`
- Articles: `quantum-computing`, `inflation-in-brazil`
- Hand-seeded claims (three per article) and citation links with evidence spans from article section text
- Eight entities and typed relationships (outgoing and incoming on the entity graph)

## Auth

- Email-only login. No password. Malformed and unknown emails return the same `401` before malformed input can reach the seeded-user lookup.
- Bearer sessions expire after 12 hours, are capped at five per user, and are stored as SHA-256 token digests. Frontend cookie name: `wikiai_token`.
- Roles: contributor, reviewer, admin, with the checks in `apps/api/app/auth.py`.
- Admins can list and revoke sessions. There is no account create/delete UI.
- Logout requires the `Authorization` header and returns `204`. No route accepts a token in a URL.
- Databases created before token hashing lose their `auth_sessions` table on startup, which invalidates any legacy raw-token session.

Full control inventory: [security](security.md).

## Read path

- Article list and detail, including `confidence_score`, `last_verified_at`, sources, sections, and timeline.
- Article pages render a claim-level trust breakdown: each claim's confidence factors (source quality, cross-source agreement, freshness, coverage, human review) and open contradiction count.
- Lexical search over seeded article text. Not OpenSearch. Not vector retrieval.
- Article chat answers from the current article body. Not a RAG pipeline over a corpus.
- Public claims, entities, JSON-LD, and paginated export routes. No auth.
- Public suggestion list (`GET /api/v1/articles/{slug}/suggestions`) returns approved records only and omits contributor email addresses.
- Browser tab titles are per-route and per-article, not a single static title.

## Write path

- Contributors submit suggestions and sources from article pages.
- Each submission creates a durable review-queue item.
- Submission text is validated server-side: blank/whitespace-only fields are rejected, and each field has a maximum length (`summary` 500, `proposed_text` 10,000, `source_url`/`url` 2,048, `rationale` 2,000, chat `question` 2,000).
- Reviewers filter by status and subject type, self-assign without taking another reviewer's work, and approve or reject with notes. Self-review is forbidden.
- Review decisions are final. A second decision on an already-decided queue item returns `409` and does not change the item's status or its subject.
- Contributors see their own submissions on `/contributors`.
- Admins see recent audit events and active sessions on `/admin`.

## Trust metadata

- Article `confidence_score` values are stored with the seed data.
- Claim `confidence` is computed as the weakest supporting citation tier (`A=0.95`, `B=0.85`, `C=0.70`, `D=0.50`). The breakdown is persisted in `confidence_metrics` and returned on each claim as `confidence_metrics`.
- `claim_citations.evidence_span` is populated from the matching article section text.
- Contradictions are stored when a new claim conflicts with another active claim on the same article (negation + token overlap) or when a citation has `support_type=contradicts`. Seeded claims have none. They appear on the claim object as `contradictions`.
- Entity graph returns outgoing relationships first, then incoming.
- The confidence breakdown and contradiction status are not API-only: article pages render them in a "Trust breakdown" panel per claim.

## Frontend fallback

`apps/web/lib/api.ts` uses `safeFetch`. When the API is unreachable or returns a non-OK status, article and search views can render bundled mock data. Treat a populated homepage as proof of the UI, not proof that the API is up. Confirm with `GET /health`.

## Not in this MVP

OpenSearch, Redis, Kubernetes, MFA, shared multi-instance rate limiting, production identity, source-ingestion workers, verification agents, and AI claim extraction.

The MVP enforces process-local limits on login, export, and contribution writes. Deployments with multiple API workers need a shared limiter. Those limits key on the socket address, so a reverse proxy collapses every caller into one bucket.

Accepted security limitations are listed in full under [security](security.md#known-limitations). Read that page before you deploy this anywhere shared.

API surface: [API reference](api.md). Product intent: [product](../explanation/product.md).
