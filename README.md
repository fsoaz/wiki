# WikiAI

WikiAI is an AI-powered encyclopedia MVP focused on transparent, evidence-backed knowledge.

## Status

This repository currently contains a functional MVP scaffold.

- It is a real working MVP with frontend, backend, persistence, auth, contributor flows, reviewer flows, and admin/audit surfaces.
- It is not yet a production-ready `v1`.
- Core gaps still include production identity, search/indexing infrastructure, source-ingestion automation, verification agents, migrations, and operational hardening.

## Applications

- `apps/web`: `Next.js` frontend for homepage, article reading, and AI search.
- `apps/api`: `FastAPI` backend with seeded article, search, and article-chat endpoints.
- `infra/sql/001_init.sql`: PostgreSQL schema for the platform data model.
- `docker-compose.yml`: local PostgreSQL service.

## MVP Features

- canonical article read experience
- grounded search results with citations
- article trust metadata: confidence, verification date, source list
- seeded article assistant endpoint
- PostgreSQL schema aligned with the product blueprint
- token-backed demo auth with contributor, reviewer, and admin roles
- contributor submission forms directly on article pages
- reviewer queue dashboard with approve/reject actions
- reviewer queue filters, self-assignment, and decision notes/history
- admin dashboard with recent audit events and workflow visibility
- admin session inspection and revocation for seeded demo accounts

## Run The MVP

### Frontend

```bash
npm install
npm run dev:web
```

### API

```bash
cd apps/api
uv sync
uv run uvicorn app.main:app --reload
```

Set `WIKIAI_DATABASE_URL` if you want PostgreSQL instead of the default local SQLite file:

```bash
export WIKIAI_DATABASE_URL=postgresql+psycopg://wikiai:wikiai@localhost:5432/wikiai
```

Demo auth accounts:

- `contributor@example.com`
- `reviewer@example.com`
- `admin@example.com`

Use the frontend sign-in route at `/signin` to create an MVP session cookie.

## Current Workflow

1. Sign in through `/signin`.
2. Contributors can submit article improvements and source proposals from article pages.
3. Reviewers can inspect `/review`, filter the queue, self-assign items, and approve or reject with notes.
4. Contributors can inspect `/contributors` to see the status of their submissions.
5. Admins can inspect `/admin` for recent audit events, active sessions, queue activity, and session revocation.

### Database

```bash
docker compose up postgres
```

The frontend expects the API at `http://localhost:8000` by default.

## Repository Structure

- `docs/context/`: product, architecture, and roadmap specifications.
- `docs/standards/`: API, AI, testing, and documentation rules.
- `docs/execution/`: task execution history and validation notes.

---
