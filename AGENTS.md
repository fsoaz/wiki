# Repository Guidelines

## Project Structure & Module Organization

`WikiAI` is a small monorepo with two apps:

- `apps/web`: Next.js frontend under `app/`, shared UI in `components/`, and client helpers in `lib/`.
- `apps/api`: FastAPI service with application code in `app/` and tests in `tests/`.
- `infra/sql/001_init.sql`: bootstrap PostgreSQL schema.
- `docs/context`, `docs/standards`, `docs/execution`: product specs, engineering rules, and execution notes.

Keep changes scoped to the app you are touching. Put cross-cutting product or process updates in `docs/`.

## Build, Test, and Development Commands

- `npm install`: install root workspace dependencies.
- `npm run dev:web`: start the frontend at `http://localhost:3000`.
- `npm run build:web`: create a production web build.
- `npm run lint:web`: run Next.js linting for `apps/web`.
- `cd apps/api && uv sync`: install API dependencies.
- `cd apps/api && uv run uvicorn app.main:app --reload`: run the API locally on `:8000`.
- `cd apps/api && uv run pytest`: run the API test suite.
- `docker compose up postgres`: start local PostgreSQL when testing against the SQL schema.

Set `WIKIAI_DATABASE_URL` to switch the API from default SQLite to PostgreSQL.

## Coding Style & Naming Conventions

Use clear operational English in docs and keep headings behavior-oriented. In code, follow the existing style:

- TypeScript/React: 2-space indentation, `PascalCase` components, `camelCase` helpers, route files inside `app/**/page.tsx`.
- Python: PEP 8, 4-space indentation, `snake_case` modules and functions.
- Prefer small, explicit modules such as `lib/api.ts`, `app/services.py`, and `app/repository.py`.

Run `npm run lint:web` before submitting frontend changes. Keep Markdown ASCII-friendly unless the file already requires otherwise.

## Testing Guidelines

API tests use `pytest` from `apps/api/tests`. Name files `test_*.py`. Add or update tests for endpoint behavior, reviewer/admin workflows, and trust metadata whenever those paths change.

There is no dedicated frontend test suite yet, so at minimum run `npm run lint:web` and manually verify affected routes such as `/signin`, `/review`, or `/admin`.

## Commit & Pull Request Guidelines

Current history uses short, imperative commit subjects, for example `Build WikiAI MVP scaffold`. Follow that pattern and keep each commit focused.

Pull requests should include a brief summary, affected areas (`apps/web`, `apps/api`, `infra`, `docs`), local test commands run, and screenshots for visible UI changes. Link the related task or issue when available.
