# API reference

Narrative companion to the generated OpenAPI schema. FastAPI serves the live schema at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

Do not hand-maintain a second OpenAPI file. If a field disagrees with `/docs`, the running app wins. Then fix this page.

## Basics

| Item | Value |
| --- | --- |
| Base URL | `http://localhost:8000` |
| Version | `0.1.0` |
| Prefix | `/api/v1` except `GET /health` |
| Auth | `Authorization: Bearer <token>` on protected routes |
| Rate limits | Single-instance limits on login, export, and contribution writes |

Login is email-only. See [Sign in and use roles](../how-to/sign-in-and-roles.md). Control inventory: [security](security.md).

## Roles

| Role | Can call |
| --- | --- |
| anonymous | Health, articles, search, article chat, public suggestion list, claims, entities, JSON-LD, export |
| contributor | Anonymous routes plus suggestion/source POST and contributor overview |
| reviewer | Contributor routes plus review queue, assignment, and decisions |
| admin | Reviewer routes plus admin overview, audit, session list, and revoke |

A reviewer token satisfies contributor checks. An admin token satisfies reviewer and contributor checks.

## Errors

These `detail` strings come from `HTTPException` in the running API.

| HTTP | `detail` | When |
| --- | --- | --- |
| 401 | `Authentication required` | Missing header, or header does not start with `Bearer ` |
| 401 | `Invalid session` | Token is not in `auth_sessions` |
| 403 | `Contributor access required` | Authenticated user role is not contributor, reviewer, or admin |
| 403 | `Reviewer access required` | Role is not reviewer or admin |
| 403 | `Admin access required` | Role is not admin |
| 401 | `Invalid credentials` | Login email is not a seeded user |
| 404 | `Article not found` | Unknown article slug |
| 404 | `Claim not found` | Unknown claim id |
| 404 | `Entity not found` | Unknown entity slug |
| 404 | `Queue item not found` | Unknown review-queue id |
| 403 | `Reviewers cannot decide on their own submissions` | Reviewer and contributor are the same account |
| 409 | `Queue item is already assigned or decided` | Review ownership or state conflicts |
| 429 | `Rate limit exceeded` | Request limit reached; see `Retry-After` |

Validation errors (malformed JSON, failed query constraints) return FastAPI's standard `422` body.

## Public read

### `GET /health`

Liveness. Example:

```bash
curl -s http://localhost:8000/health
```

```json
{"status":"ok","environment":"development"}
```

### `GET /api/v1/articles`

List article summaries (`slug`, `title`, `summary`, `confidence_score`, `last_verified_at`).

```bash
curl -s http://localhost:8000/api/v1/articles
```

### `GET /api/v1/articles/{slug}`

Full article including sections, timeline, sources, related topics, `verification_status`, and `revision_count`. Seeded slugs: `quantum-computing`, `inflation-in-brazil`.

```bash
curl -s http://localhost:8000/api/v1/articles/quantum-computing
```

### `GET /api/v1/search?q=`

Lexical search. `q` is optional, max length 200. The payload separates `answer`, `articles`, and `sources`, and includes `confidence_score`.

```bash
curl -s "http://localhost:8000/api/v1/search?q=quantum"
```

### `POST /api/v1/articles/{slug}/chat`

Article-scoped question. Body: `{"question":"..."}`. The answer is grounded in that article's seeded text.

```bash
curl -s -X POST http://localhost:8000/api/v1/articles/quantum-computing/chat \
  -H 'Content-Type: application/json' \
  -d '{"question":"What limits useful quantum computation?"}'
```

### `GET /api/v1/articles/{slug}/suggestions`

Lists approved suggestions for an article. Public responses omit contributor email addresses. Pending and rejected records remain private to contributor/reviewer views.

## Epistemic database

Public read. Realistic walkthrough: [Query claims and the knowledge graph](../how-to/query-claims-and-graph.md).

| Method | Path | Notes |
| --- | --- | --- |
| GET | `/api/v1/articles/{slug}/claims` | Claims plus citations for one article |
| GET | `/api/v1/claims/{claim_id}` | One claim and its citation chain |
| GET | `/api/v1/entities` | All entities |
| GET | `/api/v1/entities/{slug}` | Entity, outgoing then incoming relationships, linked article slugs |
| GET | `/api/v1/articles/{slug}/jsonld` | Schema.org JSON-LD for one article. `Content-Type: application/ld+json` |
| GET | `/api/v1/export?format=jsonld` | Bounded `@graph`; `limit` 1–500 (default 100), `offset` ≥0 |

```bash
curl -s http://localhost:8000/api/v1/articles/quantum-computing/claims
curl -s http://localhost:8000/api/v1/entities/quantum-computing
curl -s http://localhost:8000/api/v1/export?format=jsonld
```

MVP notes: claim `confidence` is the weakest supporting citation tier. `citations[].evidence_span` is taken from article section text. Claim responses include `confidence_metrics` and `contradictions`.

## Auth

| Method | Path | Auth |
| --- | --- | --- |
| POST | `/api/v1/auth/login` | None. Body `{"email":"contributor@example.com"}` |
| GET | `/api/v1/auth/session` | Bearer |
| POST | `/api/v1/auth/logout` | Bearer; returns HTTP 204 |

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"contributor@example.com"}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')

curl -s http://localhost:8000/api/v1/auth/session \
  -H "Authorization: Bearer $TOKEN"

curl -s -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

## Contributor

Requires a contributor, reviewer, or admin token.

| Method | Path | Body |
| --- | --- | --- |
| POST | `/api/v1/articles/{slug}/suggestions` | `suggestion_type` (`edit`, `source`, `outdated`, `correction`), `summary`, optional `proposed_text`, optional `source_url` |
| POST | `/api/v1/articles/{slug}/sources` | `title`, `publisher`, `url`, `rationale` |
| GET | `/api/v1/contributors/overview` | None. Scoped to the authenticated email |

```bash
curl -s -X POST http://localhost:8000/api/v1/articles/quantum-computing/suggestions \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"suggestion_type":"correction","summary":"Clarify error-correction overhead.","proposed_text":"Add a sentence about error-correction overhead."}'
```

Successful suggestion and source POST responses use HTTP 201. These writes are limited to 20 per authenticated user per hour.

## Reviewer

Requires a reviewer or admin token.

| Method | Path | Notes |
| --- | --- | --- |
| GET | `/api/v1/reviews/queue` | Optional `status` and `subject_type` query params |
| GET | `/api/v1/reviews/overview` | Same filters, plus counts |
| POST | `/api/v1/reviews/queue/{queue_item_id}/assign` | Self-assign |
| POST | `/api/v1/reviews/queue/{queue_item_id}/decision` | Body `{"decision":"approved"}` or `"rejected"`, optional `notes` |

`subject_type` values: `suggestion`, `source_submission`.

Review decisions are final, reviewers cannot decide their own submissions, and another reviewer's assignment cannot be seized. State or ownership conflicts return HTTP 409 without changing data.

## Admin

Requires an admin token.

| Method | Path | Notes |
| --- | --- | --- |
| GET | `/api/v1/admin/overview` | Counts plus recent audit entries |
| GET | `/api/v1/admin/audit` | `limit` 1–200 (default 50), optional `action` |
| GET | `/api/v1/admin/sessions` | `limit` 1–500 (default 100) |
| POST | `/api/v1/admin/sessions/{session_id}/revoke` | Returns `{"ok": true/false}` |

## Failure modes beyond HTTP errors

- **Frontend looks healthy while the API is down.** Article and search pages fall back to mock data. Check `/health`.
- **CORS.** Development adds both local web origins. Other environments use only the comma-separated `WIKIAI_CORS_ORIGIN` allowlist; wildcard origins are rejected.
- **Rate limits.** The limiter is process-local, and login and export buckets key on the socket address rather than `X-Forwarded-For`. Behind a reverse proxy every caller shares one bucket. Multi-worker deployments need a shared edge or Redis-backed limiter. Details: [security](security.md#known-limitations).
- **Export paging.** `limit` and `offset` bound the response body, not the work the server does to build it.

Full control inventory and accepted limitations: [security](security.md).
