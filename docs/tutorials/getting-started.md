# Get the MVP running

This tutorial takes you from a clone of the repository to a working local WikiAI: API on port 8000, website on port 3000, one seeded article in the browser.

Expect about 10 minutes if the prerequisites are already installed.

## Prerequisites

Install these tools before you start:

- Node.js 18.18 or newer
- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)

You do not need Docker for this path. The API uses SQLite by default.

## 1. Install the frontend workspace

From the repository root:

```bash
npm install
```

## 2. Install and start the API

```bash
cd apps/api
uv sync
uv run uvicorn app.main:app --reload
```

Leave this process running. On first start the API:

- creates `apps/api/wikiai.db`
- seeds demo users, two articles (`quantum-computing` and `inflation-in-brazil`), claims, and entities

Confirm it is up:

```bash
curl -s http://localhost:8000/health
```

You should see:

```json
{"status":"ok","environment":"development"}
```

Interactive API docs are at `http://localhost:8000/docs`.

## 3. Start the website

Open a second terminal at the repository root:

```bash
npm run dev:web
```

Open `http://localhost:3000`. Open `/articles/quantum-computing` and confirm the article title, sources, and confidence metadata render.

## 4. Sign in as a contributor

Open `http://localhost:3000/signin`. Choose **Continue as Contributor**. That uses `contributor@example.com`. There is no password.

You can now submit an improvement from an article page. The longer role walkthrough is [Sign in and use roles](../how-to/sign-in-and-roles.md).

## What you ran

| Process | URL | Default data |
| --- | --- | --- |
| FastAPI | `http://localhost:8000` | SQLite file `apps/api/wikiai.db` |
| Next.js | `http://localhost:3000` | Calls `http://localhost:8000` |

Next jobs:

- [Query claims and the knowledge graph](../how-to/query-claims-and-graph.md)
- [Use PostgreSQL locally](../how-to/use-postgres.md)
- [API reference](../reference/api.md)

## Troubleshooting

### The homepage still shows articles when the API is down

The frontend catches failed API calls and falls back to bundled mock articles. That is not live data.

Start the API on port 8000. If you serve the API somewhere else, set `NEXT_PUBLIC_API_URL` (see [configuration](../reference/configuration.md)) and restart `npm run dev:web`.

### `uv` or Python 3.12 is missing

The API requires Python 3.12 or newer (`requires-python = ">=3.12"` in `apps/api/pyproject.toml`). Install [uv](https://docs.astral.sh/uv/), then rerun `uv sync` from `apps/api`.

### Sign-in fails or dashboards stay empty

1. Confirm `curl -s http://localhost:8000/health` works.
2. Use `http://localhost:3000`, not a different origin, unless you also set `WIKIAI_CORS_ORIGIN`. The API allows `http://localhost:3000` by default and also `http://127.0.0.1:3000`.
3. Sign-in is email-only against the three seeded accounts. An unknown email returns `401` with `Invalid credentials`.
