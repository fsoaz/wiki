# API reference

Narrative companion to the generated OpenAPI schema. FastAPI serves the live schema at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

Do not hand-maintain a second OpenAPI file. FastAPI source and the generated schema at `/openapi.json` are the behavior contract. This page is the canonical narrative companion. If they disagree, update this page in the same pull request.

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
| 401 | `Authentication required` | Missing header, or header does not start with `Bearer` followed by a space |
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

## Endpoint contract index

This index makes the request, successful response, expected failures, and rate limit discoverable for every route. `None` means the route has no request body and no endpoint-specific limit. Response model names link to a realistic example below; `/openapi.json` remains exhaustive for every field and validation rule.

| Endpoint | Request example | Success and response example | Expected failures | Rate limit |
| --- | --- | --- | --- | --- |
| `GET /health` | None | `200` [health](#health-response) | None | None |
| `POST /api/v1/auth/login` | `{"email":"contributor@example.com"}` | `200` [session](#session-response) | `401`, `422`, `429` | 5/IP/minute |
| `GET /api/v1/auth/session` | Bearer token | `200` [user](#user-response) | `401` | None |
| `POST /api/v1/auth/logout` | Bearer token | `204` with no body | `401` | None |
| `GET /api/v1/articles` | None | `200` [article summaries](#article-summary-response) | None | None |
| `GET /api/v1/articles/{slug}` | `quantum-computing` | `200` [article](#article-response) | `404` | None |
| `GET /api/v1/search` | `?q=quantum` | `200` [search](#search-response) | `422` | None |
| `POST /api/v1/articles/{slug}/chat` | `{"question":"What limits useful quantum computation?"}` | `200` [chat](#chat-response) | `404`, `422` | None |
| `GET /api/v1/articles/{slug}/suggestions` | `quantum-computing` | `200` [public suggestions](#public-suggestions-response) | `404` | None |
| `GET /api/v1/articles/{slug}/claims` | `quantum-computing` | `200` [claims](#claims-response) | `404` | None |
| `GET /api/v1/claims/{claim_id}` | Claim UUID | `200` [claim](#claim-response) | `404` | None |
| `GET /api/v1/entities` | None | `200` [entities](#entities-response) | None | None |
| `GET /api/v1/entities/{slug}` | `quantum-computing` | `200` [entity graph](#entity-graph-response) | `404` | None |
| `GET /api/v1/articles/{slug}/jsonld` | `quantum-computing` | `200` [article JSON-LD](#article-json-ld-response) | `404` | None |
| `GET /api/v1/export` | `?format=jsonld&limit=100&offset=0` | `200` [export JSON-LD](#export-json-ld-response), headers `X-Total-Count` and optional `Link` | `422`, `429` | 10/IP/minute |
| `POST /api/v1/articles/{slug}/suggestions` | [suggestion request](#suggestion-request) | `201` [suggestion](#suggestion-response) | `401`, `403`, `404`, `422`, `429` | 20/user/hour |
| `POST /api/v1/articles/{slug}/sources` | [source request](#source-request) | `201` [source submission](#source-submission-response) | `401`, `403`, `404`, `422`, `429` | 20/user/hour |
| `GET /api/v1/contributors/overview` | Bearer token | `200` [contributor overview](#contributor-overview-response) | `401`, `403` | None |
| `GET /api/v1/reviews/queue` | Bearer token; optional `?status=pending&subject_type=suggestion` | `200` [review queue](#review-queue-response) | `401`, `403` | None |
| `GET /api/v1/reviews/overview` | Bearer token; optional queue filters | `200` [reviewer overview](#reviewer-overview-response) | `401`, `403` | None |
| `POST /api/v1/reviews/queue/{queue_item_id}/assign` | Bearer token | `200` [assignment](#assignment-response) | `401`, `403`, `404`, `409` | None |
| `POST /api/v1/reviews/queue/{queue_item_id}/decision` | `{"decision":"approved","notes":"Evidence is sufficient."}` | `200` [decision](#decision-response) | `401`, `403`, `404`, `409`, `422` | None |
| `GET /api/v1/admin/overview` | Admin Bearer token | `200` [admin overview](#admin-overview-response) | `401`, `403` | None |
| `GET /api/v1/admin/audit` | Admin Bearer token; optional `?limit=50&action=login` | `200` [audit entries](#audit-entries-response) | `401`, `403`, `422` | None |
| `GET /api/v1/admin/sessions` | Admin Bearer token; optional `?limit=100` | `200` [session list](#session-list-response) | `401`, `403`, `422` | None |
| `POST /api/v1/admin/sessions/{session_id}/revoke` | Admin Bearer token | `200` [revoke result](#revoke-result-response) | `401`, `403` | None |

### Request examples

#### Suggestion request

```json
{"suggestion_type":"correction","summary":"Clarify error-correction overhead.","proposed_text":"Add a sentence about error-correction overhead."}
```

#### Source request

```json
{"title":"Quantum computing overview","publisher":"National Institute of Standards and Technology","url":"https://www.nist.gov/quantum-information-science","rationale":"Use this primary source to support the introductory section."}
```

### Response examples

The examples omit volatile IDs and timestamps only when they do not affect the shape. All fields appear in generated OpenAPI schemas.

#### Health response

```json
{"status":"ok","environment":"development"}
```

#### User response

```json
{"id":"user-id","email":"contributor@example.com","display_name":"Contributor","role":"contributor"}
```

#### Session response

```json
{"token":"wikiai_example","expires_at":"2026-09-05T12:00:00+00:00","user":{"id":"user-id","email":"contributor@example.com","display_name":"Contributor","role":"contributor"}}
```

#### Article summary response

```json
[{"slug":"quantum-computing","title":"Quantum Computing","summary":"An introduction to quantum computing.","confidence_score":0.86,"last_verified_at":"2026-06-01"}]
```

#### Article response

```json
{"slug":"quantum-computing","title":"Quantum Computing","summary":"An introduction to quantum computing.","confidence_score":0.86,"last_verified_at":"2026-06-01","verification_status":"verified","related_topics":["Cryptography"],"sections":[{"heading":"Overview","content":"Quantum computing uses quantum-mechanical effects.","citations":["source-id"]}],"timeline":[],"sources":[{"id":"source-id","title":"Quantum computing overview","publisher":"National Institute of Standards and Technology","tier":"A","url":"https://www.nist.gov/quantum-information-science","published_at":"2024-01-01"}],"revision_count":1}
```

#### Search response

```json
{"answer":"Quantum computing uses quantum-mechanical effects to process information.","confidence_score":0.86,"sources":[],"articles":[{"slug":"quantum-computing","title":"Quantum Computing","summary":"An introduction to quantum computing.","confidence_score":0.86,"last_verified_at":"2026-06-01"}]}
```

#### Chat response

```json
{"answer":"Useful quantum computation is limited by noise and error-correction overhead.","confidence_score":0.86,"citations":[],"reasoning":["Answer derived from the article content."]}
```

#### Public suggestions response

```json
[{"id":"suggestion-id","article_slug":"quantum-computing","contributor_name":"Contributor","suggestion_type":"correction","summary":"Clarify error-correction overhead.","proposed_text":"Add a sentence about error-correction overhead.","source_url":null,"status":"approved","created_at":"2026-09-04T12:00:00+00:00"}]
```

#### Claims response

```json
[{"id":"claim-id","article_slug":"quantum-computing","claim_text":"Quantum computers use qubits.","claim_type":"factual","section_key":"overview","status":"active","confidence":0.95,"citations":[{"id":"citation-id","source_id":"source-id","evidence_span":"Quantum computers use qubits.","support_type":"supports"}],"confidence_metrics":{"id":"metric-id","subject_type":"claim","subject_id":"claim-id","overall_score":0.95,"source_quality_score":0.95,"cross_source_agreement_score":1.0,"freshness_score":1.0,"coverage_score":1.0,"human_review_score":1.0,"computed_at":"2026-09-04T12:00:00+00:00"},"contradictions":[]}]
```

#### Claim response

The claim endpoint returns one object with the same shape as an item in [claims response](#claims-response).

#### Entities response

```json
[{"id":"entity-id","name":"Quantum computing","entity_type":"technology","canonical_slug":"quantum-computing","description":"A computing paradigm that uses quantum effects."}]
```

#### Entity graph response

```json
{"entity":{"id":"entity-id","name":"Quantum computing","entity_type":"technology","canonical_slug":"quantum-computing","description":"A computing paradigm that uses quantum effects."},"relationships":[{"id":"relationship-id","subject_slug":"quantum-computing","subject_name":"Quantum computing","predicate":"uses","object_slug":"qubit","object_name":"Qubit","confidence":0.95}],"article_slugs":["quantum-computing"]}
```

#### Article JSON-LD response

```json
{"@context":"https://schema.org","@type":"Article","@id":"/articles/quantum-computing","name":"Quantum Computing","description":"An introduction to quantum computing.","dateModified":"2026-06-01","creditText":"confidence:0.86","articleSection":[],"citation":[]}
```

#### Export JSON-LD response

```json
{"@context":"https://schema.org","@graph":[]}
```

#### Suggestion response

The successful response has the [public suggestion](#public-suggestions-response) shape plus `contributor_email`.

#### Source submission response

```json
{"id":"source-submission-id","article_slug":"quantum-computing","contributor_name":"Contributor","contributor_email":"contributor@example.com","title":"Quantum computing overview","publisher":"National Institute of Standards and Technology","url":"https://www.nist.gov/quantum-information-science","rationale":"Use this primary source to support the introductory section.","status":"pending","created_at":"2026-09-04T12:00:00+00:00"}
```

#### Contributor overview response

```json
{"contributor_email":"contributor@example.com","suggestion_count":1,"source_submission_count":0,"suggestions":[],"source_submissions":[]}
```

#### Review queue response

```json
[{"id":"queue-id","article_slug":"quantum-computing","article_title":"Quantum Computing","subject_type":"suggestion","subject_id":"suggestion-id","priority":"normal","status":"pending","assigned_reviewer_email":null,"summary":"Clarify error-correction overhead.","contributor_name":"Contributor","contributor_email":"contributor@example.com","created_at":"2026-09-04T12:00:00+00:00","decisions":[]}]
```

#### Reviewer overview response

```json
{"pending_count":1,"approved_count":0,"rejected_count":0,"items":[]}
```

#### Assignment response

```json
{"queue_item_id":"queue-id","assigned_reviewer_email":"reviewer@example.com","status":"pending"}
```

#### Decision response

```json
{"id":"decision-id","queue_item_id":"queue-id","reviewer_email":"reviewer@example.com","decision":"approved","notes":"Evidence is sufficient.","created_at":"2026-09-04T12:00:00+00:00"}
```

#### Admin overview response

```json
{"audit_event_count":1,"review_queue_count":1,"active_session_count":1,"recent_audit_entries":[]}
```

#### Audit entries response

```json
[{"id":"audit-id","actor_email":"admin@example.com","actor_role":"admin","action":"session_revoked","subject_type":"auth_session","subject_id":"session-id","details_json":"{}","created_at":"2026-09-04T12:00:00+00:00"}]
```

#### Session list response

```json
[{"id":"session-id","user_email":"contributor@example.com","user_role":"contributor","expires_at":"2026-09-05T12:00:00+00:00","created_at":"2026-09-04T12:00:00+00:00"}]
```

#### Revoke result response

```json
{"ok":true}
```

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
