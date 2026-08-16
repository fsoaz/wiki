# Configuration

Environment variables for the local MVP. There is no secrets manager in this build. Security behavior these variables drive: [security](security.md).

## API (`apps/api`)

Settings load from [apps/api/app/config.py](../../apps/api/app/config.py) with prefix `WIKIAI_`. Unknown env vars are ignored.

| Variable | Default | Purpose |
| --- | --- | --- |
| `WIKIAI_APP_NAME` | `WikiAI API` | OpenAPI title |
| `WIKIAI_APP_ENV` | `development` | Returned by `GET /health` as `environment` |
| `WIKIAI_CORS_ORIGIN` | `http://localhost:3000` | Comma-separated CORS allowlist. `*` is rejected; local origins are added only in development |
| `WIKIAI_DATABASE_URL` | `sqlite:///./wikiai.db` | SQLAlchemy URL. SQLite relative paths resolve from the process working directory (`apps/api` if you start uvicorn there) |
| `WIKIAI_SESSION_TTL_HOURS` | `12` | Absolute bearer-session lifetime |
| `WIKIAI_MAX_SESSIONS_PER_USER` | `5` | Maximum live sessions retained per seeded user |

Postgres example:

```bash
export WIKIAI_DATABASE_URL=postgresql+psycopg://wikiai:wikiai@localhost:5432/wikiai
```

See [Use PostgreSQL locally](../how-to/use-postgres.md).

### Settings with no environment variable

- **Rate limits** are compiled in at `apps/api/app/main.py`: login 5 per minute per client IP, export 10 per minute per client IP, contribution writes 20 per hour per authenticated email. Change them in code.
- **Client IP** comes from the socket address. The API ignores `X-Forwarded-For`, so a reverse proxy makes every caller share one bucket. There is no trusted-proxy setting yet. See [security](security.md#rate-limits-key-on-the-socket-address).

> **Danger:** Do not put the runtime database under version control. `.gitignore` covers `apps/api/*.db`, and `auth_sessions` rows are live session material.

## Web (`apps/web`)

| Variable | Default | Purpose |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Browser and server-side fetch base URL |

Restart `npm run dev:web` after you change `NEXT_PUBLIC_API_URL`. Next.js inlines `NEXT_PUBLIC_*` values at startup.

> **Warning:** If this URL is wrong, article pages still render. The client falls back to mock articles. That looks like success and is not live API data.
