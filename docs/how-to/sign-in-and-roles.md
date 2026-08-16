# Sign in and use roles

WikiAI MVP auth is [demo auth](../glossary.md#demo-auth): three seeded emails, no password, bearer-token sessions.

> **Warning:** Do not treat this as production identity. There is no password, MFA, or account lifecycle beyond session revocation.

## Seeded accounts

| Email | Role | What they can do |
| --- | --- | --- |
| `contributor@example.com` | contributor | Submit suggestions and sources; view `/contributors` |
| `reviewer@example.com` | reviewer | Everything a contributor can do, plus `/review` |
| `admin@example.com` | admin | Reviewer access plus `/admin` session and audit tools |

Role checks live in `apps/api/app/auth.py`. Admins and reviewers satisfy contributor checks. Admins satisfy reviewer checks.

## Sign in from the website

1. Start the API and web app ([getting started](../tutorials/getting-started.md)).
2. Open `http://localhost:3000/signin`.
3. Click **Continue as Contributor**, **Reviewer**, or **Admin**.

The page `POST`s `{"email":"..."}` to `/api/v1/auth/login` and stores the returned token in a 12-hour HTTP-only cookie named `wikiai_token`. The cookie is `Secure` in production. Later server-side requests send `Authorization: Bearer <token>`.

## Sign in from the API

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"reviewer@example.com"}'
```

The response includes `token`, `expires_at`, and `user`. The database stores only a SHA-256 digest of the token. Call protected routes with the raw token as a Bearer secret:

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"reviewer@example.com"}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])')

curl -s http://localhost:8000/api/v1/auth/session \
  -H "Authorization: Bearer $TOKEN"
```

## Logout

The website **Clear local session** control revokes the API session and then deletes the `wikiai_token` cookie. The API expects the Bearer header:

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

A valid session is deleted and returns HTTP 204. Missing, invalid, or expired tokens return HTTP 401.

## Failure modes

| What you did | What you get |
| --- | --- |
| Malformed email (no `@`, no domain) | `401` `Invalid credentials`, before the seeded-user lookup runs |
| Unknown but well-formed email | `401` `Invalid credentials` |
| Missing or non-Bearer `Authorization` header on a protected route | `401` `Authentication required` |
| Unknown or expired token | `401` `Invalid session` |
| Contributor token on a reviewer route | `403` `Reviewer access required` |
| Non-admin token on an admin route | `403` `Admin access required` |

Full error catalog: [API reference](../reference/api.md#errors).
