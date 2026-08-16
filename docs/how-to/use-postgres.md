# Use PostgreSQL locally

By default the API stores data in SQLite at `apps/api/wikiai.db`. Use this guide when you want the Postgres service from `docker-compose.yml`.

## Prerequisites

- Docker
- The API dependencies from [Get the MVP running](../tutorials/getting-started.md)

## 1. Start Postgres

From the repository root:

```bash
docker compose up postgres
```

Compose starts `postgres:17` with:

- database `wikiai`
- user `wikiai`
- password `wikiai`
- port `5432`

On first boot it runs SQL files from `infra/sql/` as init scripts, including [infra/sql/001_init.sql](../../infra/sql/001_init.sql).

## 2. Point the API at Postgres

```bash
export WIKIAI_DATABASE_URL=postgresql+psycopg://wikiai:wikiai@localhost:5432/wikiai
```

Then start the API from `apps/api`:

```bash
uv run uvicorn app.main:app --reload
```

Restart the process after you change `WIKIAI_DATABASE_URL`. Settings load from the environment prefix `WIKIAI_`. See [configuration](../reference/configuration.md).

## 3. Confirm the connection

```bash
curl -s http://localhost:8000/health
```

Then list articles:

```bash
curl -s http://localhost:8000/api/v1/articles
```

You should see `quantum-computing` and `inflation-in-brazil`. Startup still seeds users, articles, claims, and entities when those tables are empty.

## SQLite versus Postgres schema

- **SQLite (default):** SQLAlchemy `create_all` builds tables from the ORM models in `apps/api/app/db_models.py`.
- **Postgres:** `infra/sql/001_init.sql` is the bootstrap schema Compose loads into a new volume.

Those two sources can drift. If a seed or query fails against Postgres, compare the ORM models with `001_init.sql`.

## Troubleshooting

- **Port 5432 already in use:** stop the other Postgres, or change the host port in `docker-compose.yml`.
- **API still using SQLite:** the URL must start with `postgresql+psycopg://`. Check the environment of the shell that launched uvicorn.
- **Empty database after a volume reset:** Compose re-runs `infra/sql/` only on a new volume. The API seed runs on startup when tables have no users or articles.
