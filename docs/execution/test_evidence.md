# Test Evidence

## 2026-06-13

Validation performed:

- confirmed API import succeeds: `uv run python -c "from app.main import app; print('import OK')"`
- started API: `uv run uvicorn app.main:app --port 8002 --log-level warning`
- confirmed `GET /health` returns `{"status":"ok","environment":"development"}`
- confirmed `GET /api/v1/articles/quantum-computing/claims` returns 3 atomic claims with `claim_type`, `confidence`, and citation arrays
- confirmed `GET /api/v1/entities` returns 8 entities with `entity_type` and `canonical_slug`
- confirmed `GET /api/v1/entities/quantum-computing` returns entity with 3 typed outgoing relationships and linked `article_slugs`
- confirmed `GET /api/v1/articles/quantum-computing/jsonld` returns valid Schema.org JSON-LD with `@context`, `articleSection`, and `citation` arrays

Not performed:

- test suite update for new endpoints (existing tests unaffected)
- end-to-end browser testing of new endpoints via frontend
- live PostgreSQL integration tests
- OpenSearch or vector retrieval integration tests

## 2026-06-07

Validation performed:

- confirmed all target documentation files existed and were writable
- verified the repository had no pre-existing implementation content that would conflict with the new blueprint
- reviewed the resulting file set through patch application consistency
- ran `npm install` successfully at repository root
- ran `uv sync --group dev` in `apps/api` with `UV_CACHE_DIR=/tmp/uv-cache`
- ran backend tests: `UV_CACHE_DIR=/tmp/uv-cache .venv/bin/pytest -q`
- ran frontend type-check: `npx tsc --noEmit` in `apps/web`
- ran frontend production build: `npm run build:web`
- reran backend dependency sync after adding persistence packages: `UV_CACHE_DIR=/tmp/uv-cache uv sync --group dev`
- reran backend tests after the SQLAlchemy persistence refactor: `UV_CACHE_DIR=/tmp/uv-cache .venv/bin/pytest -q`
- reran backend tests after contributor workflow expansion: `UV_CACHE_DIR=/tmp/uv-cache .venv/bin/pytest -q`
- reran frontend type-check after dashboard additions: `npx tsc --noEmit`
- reran frontend production build after dashboard additions: `npm run build:web`
- reran backend tests after reviewer workflow expansion: `UV_CACHE_DIR=/tmp/uv-cache .venv/bin/pytest -q`
- reran frontend type-check after reviewer dashboard additions: `npx tsc --noEmit`
- reran frontend production build after reviewer dashboard additions: `npm run build:web`
- reran backend tests after auth and RBAC rollout: `UV_CACHE_DIR=/tmp/uv-cache .venv/bin/pytest -q`
- reran frontend type-check after sign-in and protected route updates: `npx tsc --noEmit`
- reran frontend production build after sign-in and protected route updates: `npm run build:web`
- reran backend tests after UI submission and review actions: `UV_CACHE_DIR=/tmp/uv-cache .venv/bin/pytest -q`
- reran frontend type-check after article-page forms and review actions: `npx tsc --noEmit`
- reran frontend production build after article-page forms and review actions: `npm run build:web`
- reran backend tests after review queue UX expansion: `UV_CACHE_DIR=/tmp/uv-cache .venv/bin/pytest -q`
- reran frontend type-check after queue filters, assignment, and history UI: `npx tsc --noEmit`
- reran frontend production build after queue filters, assignment, and history UI: `npm run build:web`
- reran backend tests after admin audit logging and dashboard additions: `UV_CACHE_DIR=/tmp/uv-cache .venv/bin/pytest -q`
- reran frontend type-check after admin dashboard additions: `npx tsc --noEmit`
- reran frontend production build after admin dashboard additions: `npm run build:web`
- reran backend tests after admin session management additions: `UV_CACHE_DIR=/tmp/uv-cache .venv/bin/pytest -q`
- reran frontend type-check after admin session controls: `npx tsc --noEmit`
- reran frontend production build after admin session controls: `npm run build:web`

Not performed:

- end-to-end browser testing
- live database integration tests
- OpenSearch or vector retrieval integration tests
