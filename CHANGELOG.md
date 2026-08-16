# Changelog

Human-readable history of WikiAI. Dates are when the change landed in this repository. Commit messages are not a substitute for this file.

## Unreleased

### Added

- Claim `confidence` is computed from the weakest supporting citation tier and returned with a `confidence_metrics` breakdown.
- `claim_citations.evidence_span` is populated from matching article section text.
- Entity graph includes incoming relationships after outgoing ones.
- JSON-LD routes (`/api/v1/articles/{slug}/jsonld`, `/api/v1/export`) return `Content-Type: application/ld+json`.
- Contradiction records are stored on claim create (negated same-article claims, or `support_type=contradicts` citations) and returned on the claim object.

### Changed

- Runtime SQLite databases are ignored; legacy raw-token sessions are invalidated during the session-schema upgrade.
- Bearer sessions are hashed at rest, expire after 12 hours, and are capped at five per user; logout now uses the Authorization header.
- Reviewer self-approval and assignment takeover are blocked with atomic state checks.
- Login, JSON-LD export, and contribution writes have process-local rate limits; export is paginated.
- CORS uses a validated environment-specific allowlist, and audit details use safe JSON serialization.
- Sign-in redirects are restricted to same-origin paths and production session cookies use `Secure`.
- Public suggestions include approved content only; search handles empty databases and literal wildcard characters safely.
- Reviewer decisions are final; repeat attempts return a conflict without changing state.
- Public suggestion responses omit contributor email addresses.
- Contribution payloads reject blank or oversized text, and login rejects malformed email addresses.
- Article pages show claim confidence factors and contradiction status.
- Browser-tab titles identify each application route and article.

### Documentation

- [Security reference](docs/reference/security.md): trust boundaries, the controls the running code enforces, accepted limitations, and the checklist that blocks a production deployment.
- Rate-limit documentation now states that limits key on the socket address, so a reverse proxy collapses every caller into one bucket, and that export paging bounds the response rather than the server's work.
- Diátaxis docs tree: tutorials, how-to guides, reference, and explanation.
- README hub (what, install, run, contribute), CONTRIBUTING.md, glossary, and API narrative around FastAPI OpenAPI. Index: [docs/README.md](docs/README.md).
- Target architecture separated from shipped MVP behavior.

## 0.1.0 - 2026-06-13

MVP scaffold. Not a production release.

### Added

- Article read, lexical search, and article-scoped chat over seeded content (`quantum-computing`, `inflation-in-brazil`).
- Demo auth: email-only login for `contributor@example.com`, `reviewer@example.com`, and `admin@example.com`.
- Contributor suggestions and source submissions with a durable review queue.
- Reviewer filters, self-assignment, decision notes, and history.
- Contributor dashboard and admin audit/session tools.
- Atomic claims, entities, typed relationships, and JSON-LD export (`/api/v1/articles/{slug}/claims`, `/api/v1/claims/{id}`, `/api/v1/entities`, `/api/v1/entities/{slug}`, `/api/v1/articles/{slug}/jsonld`, `/api/v1/export?format=jsonld`).
- Local SQLite by default, optional Postgres via `WIKIAI_DATABASE_URL` and `docker compose up postgres`.
