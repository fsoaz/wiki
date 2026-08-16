# Security

Exhaustive list of the security controls **the running code implements**, plus the limitations it does not cover. Target controls that are not built yet live in [target architecture](../explanation/architecture.md#security-architecture). Do not read that section as a description of this build.

Auth in this MVP is [demo auth](../glossary.md#demo-auth). It is not production identity.

> **Danger:** Do not put real user data in a WikiAI MVP deployment. Login requires no password, so knowing a seeded email address is enough to obtain that account's role.

## Trust boundaries

```text
browser  --(1)-->  apps/web (Next.js server)  --(2)-->  apps/api (FastAPI)  --(3)-->  database
```

| # | Boundary | What crosses it | Control |
| --- | --- | --- | --- |
| 1 | Browser to web server | Form posts, `wikiai_token` cookie | `HttpOnly` cookie, Next.js Server Action origin checks, same-origin redirect allowlist |
| 2 | Web server to API | `Authorization: Bearer <token>` | Bearer session lookup, role dependencies, rate limits |
| 3 | API to database | SQLAlchemy Core statements | Bound parameters on every query; no string-built SQL |

The browser never calls `apps/api` directly. `apps/web/lib/api.ts` reads the cookie server-side and attaches the Bearer header, so the raw token never reaches client JavaScript.

## Authentication and sessions

- Login accepts an email only. Malformed and unknown emails both return `401` `Invalid credentials`, so the endpoint does not confirm which addresses exist.
- Tokens are `wikiai_` plus `secrets.token_urlsafe(32)`.
- The database stores only a SHA-256 digest in `auth_sessions.token_hash`. There is no column that holds a usable token.
- Sessions carry an absolute `expires_at`. `WIKIAI_SESSION_TTL_HOURS` sets it, default `12`. There is no sliding renewal.
- `get_user_by_token` filters on `expires_at > now`, so an expired token fails closed and returns `401` `Invalid session`.
- Each login keeps at most `WIKIAI_MAX_SESSIONS_PER_USER` sessions, default `5`, and deletes the oldest beyond that.
- Login also deletes every globally expired session row.
- Logout requires the `Authorization` header, deletes the session, and returns `204`. No token is ever accepted in a URL.
- On startup, `apps/api/app/schema.py` drops any legacy `auth_sessions` table that still has a raw `token` column. Databases created before token hashing self-invalidate on first boot.

> **Warning:** `users.password_hash` exists in `apps/api/app/db_models.py` and `infra/sql/001_init.sql`, but no code writes or reads it. The column is a placeholder for the target design. Its presence does not mean the API checks passwords.

Frontend cookie attributes, set in `apps/web/app/signin/page.tsx`:

| Attribute | Value |
| --- | --- |
| `HttpOnly` | always |
| `Secure` | when `NODE_ENV` is `production` |
| `SameSite` | `Lax` |
| `Path` | `/` |
| `Expires` | the API's `expires_at`, so the cookie and the session die together |

## Authorization

- Role checks live in `apps/api/app/auth.py` as FastAPI dependencies: `require_contributor`, `require_reviewer`, `require_admin`.
- Roles nest. An admin token satisfies reviewer and contributor checks. A reviewer token satisfies contributor checks.
- A reviewer cannot decide their own submission. When the queue item's contributor email equals the caller's email, the API returns `403` `Reviewers cannot decide their own submissions`.
- A reviewer cannot take an item assigned to someone else. Assignment and decision both run a conditional `UPDATE ... WHERE status = 'pending' AND (assigned_reviewer_email IS NULL OR assigned_reviewer_email = :caller)` and return `409` when the row count is not `1`.
- `GET /api/v1/contributors/overview` is scoped to the authenticated email and cannot be pointed at another account.
- `GET /api/v1/articles/{slug}/suggestions` is public, so it returns approved records only and omits `contributor_email`. Pending and rejected text stays inside reviewer and contributor views.

## Rate limits

`apps/api/app/rate_limit.py` implements a fixed-window counter held in process memory.

| Scope | Key | Limit |
| --- | --- | --- |
| Login | Client IP | 5 per 60 seconds |
| JSON-LD export | Client IP | 10 per 60 seconds |
| Suggestion and source writes | Authenticated email | 20 per 3600 seconds |

Exceeding a limit returns `429` `Rate limit exceeded` with a `Retry-After` header. See [Known limitations](#known-limitations) before you rely on these in a deployment.

## Input handling

- Every database query uses SQLAlchemy Core constructs with bound parameters. No endpoint builds SQL from strings.
- Search escapes `\`, `%`, and `_` in the user query and passes `escape="\\"` to `ilike`, so wildcard characters match literally.
- Search returns an empty result set instead of raising when no articles exist.
- Pydantic models constrain every write. `Literal` types bound `decision`, `suggestion_type`, and `role`. Length caps: `summary` 500, `proposed_text` 10,000, `source_url` and `url` 2,048, `rationale` 2,000, chat `question` 2,000, search `q` 200.
- Blank and whitespace-only values are rejected by field validators.
- `GET /api/v1/export` requires `format=jsonld` by pattern and bounds `limit` to 1-500 and `offset` to `>= 0`.

## Redirects

`apps/web/lib/navigation.ts` exports `safeNextPath`. Sign-in applies it to the `next` parameter at both render time and inside the Server Action. A value survives only when it is a single-slash-prefixed local path. The helper rejects protocol-relative paths (`//host`), backslashes, control characters, and any percent-encoded form of those.

## CORS

Configured in `apps/api/app/main.py`:

| Setting | Value |
| --- | --- |
| `allow_origins` | `WIKIAI_CORS_ORIGIN` allowlist. Local origins are added only when `WIKIAI_APP_ENV` is `development`, and stripped otherwise |
| `allow_credentials` | `False`. The API authenticates with Bearer tokens, not cookies |
| `allow_methods` | `GET`, `POST` |
| `allow_headers` | `Authorization`, `Content-Type` |
| `expose_headers` | `Link`, `Retry-After`, `X-Total-Count` |

A `*` in `WIKIAI_CORS_ORIGIN` raises a validation error at startup. The process refuses to boot rather than serve a permissive policy.

## Audit trail

- `audit_logs` records login, logout, suggestion create, source create, assignment, review decision, and admin session revocation.
- Every `details_json` value is produced by `json.dumps`. No audit field is built by string interpolation, so contributor-controlled text cannot forge log structure.
- `GET /api/v1/admin/audit` and `GET /api/v1/admin/sessions` require an admin token. Session listings exclude expired rows.

## Data in the repository

The runtime SQLite database is **not** tracked. `.gitignore` covers `apps/api/*.db`, `apps/api/*.db-wal`, and `apps/api/*.db-shm`.

> **Danger:** Never commit `apps/api/wikiai.db`. It holds `auth_sessions` rows. A committed database publishes live session material to everyone with repository access, and git history keeps it after you delete the file.

Verify before you commit:

```bash
git ls-files --error-unmatch apps/api/wikiai.db 2>/dev/null \
  && echo "TRACKED - remove it" \
  || echo "untracked - ok"
```

## Known limitations

These are accepted for the MVP and recorded here so nobody rediscovers them as new findings.

### Rate limits key on the socket address

`_client_ip` in `apps/api/app/main.py` reads `request.client.host` and ignores `X-Forwarded-For`. That is correct when the API is exposed directly and wrong behind a reverse proxy, where every caller collapses into one bucket and the login limit becomes a global 5 per minute for all users.

Trusting the header instead would let any caller spoof a key, so the fix is an explicit trusted-hop count rather than a blanket switch. Neither behavior is configurable today.

### The limiter evicts its own oldest key

The counter caps its key table at 10,000 entries and evicts in insertion order. A caller who inserts enough distinct keys can evict their own limited entry and reset it. Reaching that state needs roughly 10,000 distinct source addresses, which already grants more attempts than the bypass returns, so the practical exposure is small. It matters most as a way to clear another key, such as a contributor's write bucket.

### Export pagination bounds the response, not the work

`GET /api/v1/export` builds the entire `@graph` and then slices it. `limit` and `offset` shape what you receive; the server still assembles every article and entity per request. The 10-per-minute limit caps the amplification. Push paging into the query before the corpus grows.

### The limiter is process-local

Counters live in one process. Running multiple API workers multiplies every limit by the worker count. Multi-instance deployments need a shared limiter.

### Expired rows persist until the next login

Expired sessions are purged inside `create_auth_session`. They cannot authenticate, and admin views hide them, but rows accumulate when logins stop. There is no scheduled sweep.

### No transport security in this repository

Nothing here terminates TLS or sets HSTS. `Secure` cookies depend on the deployment serving HTTPS.

## Before a production deployment

Demo auth is the blocking item. In rough order:

1. Replace email-only login with a real credential (Argon2id) or an OIDC provider, and require MFA for reviewer and admin roles.
2. Terminate TLS, enable HSTS, and confirm `Secure` cookies are actually set.
3. Configure trusted-proxy handling for client IPs, then move rate limiting to a shared store.
4. Add a Content-Security-Policy. `apps/web/next.config.ts` currently sets no headers.
5. Run both containers as a non-root `USER` and pin base image digests.
6. Replace the Compose Postgres credentials (`wikiai` / `wikiai`), which are development-only.
7. Define retention for `audit_logs` and an erasure path for contributor personal data.

## Reporting a problem

Open an issue describing the affected route and the observed behavior. Do not include live tokens, cookie values, or database files in the report. Contribution rules: [CONTRIBUTING.md](../../CONTRIBUTING.md).
