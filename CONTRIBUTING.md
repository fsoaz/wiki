# Contributing to WikiAI

This repository is a small monorepo. Keep each change scoped to the app you are touching. Put cross-cutting product or process updates in `docs/`.

## Before you start

1. Follow [Get the MVP running](docs/tutorials/getting-started.md).
2. Read [current MVP behavior](docs/reference/current-mvp.md) so you do not document or implement target-only features as if they already shipped.
3. Follow [documentation conventions](docs/standards/conventions.md) when you edit Markdown.

Agent-oriented repository rules live in [AGENTS.md](AGENTS.md).

## Make a change

1. Create a focused branch.
2. Change code and the docs that describe it in the same pull request. Do not leave a "docs PR coming later."
3. Keep commits short and imperative, for example `Add review queue filters`.

### Frontend (`apps/web`)

- TypeScript and React, 2-space indentation.
- `PascalCase` components, `camelCase` helpers, route files in `app/**/page.tsx`.
- Run `npm run lint:web` before you submit.
- There is no frontend test suite yet. Manually verify affected routes such as `/signin`, `/review`, or `/admin`.

### API (`apps/api`)

- Python 3.12, PEP 8, 4-space indentation, `snake_case` modules and functions.
- Add or update `apps/api/tests/test_*.py` when endpoint, reviewer, admin, or trust-metadata behavior changes.
- Run tests:

```bash
cd apps/api
uv run pytest
```

### Docs

- Write in Markdown. Put learning content in `docs/tutorials/`, goal-oriented steps in `docs/how-to/`, exhaustive facts in `docs/reference/`, and conceptual material in `docs/explanation/`.
- Update [CHANGELOG.md](CHANGELOG.md) when user-visible API or workflow behavior changes.
- Define jargon on first use, or link to the [glossary](docs/glossary.md).

## Pull requests

Include:

- a brief summary
- affected areas (`apps/web`, `apps/api`, `infra`, `docs`)
- local test commands you ran
- screenshots for visible UI changes

Link the related task or issue when one exists.
