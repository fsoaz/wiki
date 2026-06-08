# Current Task

Implement the WikiAI MVP as a runnable repository scaffold with:

- `Next.js` frontend for homepage, search, and article reading
- `FastAPI` backend for seeded article, search, and article-chat endpoints
- PostgreSQL schema bootstrap for the documented WikiAI data model
- local developer run instructions and validation evidence

Current implementation focus:

- replace in-memory API reads with database-backed persistence
- seed canonical MVP articles into the database at startup
- add durable contributor suggestion submission for articles
- add durable source submission and contributor activity visibility
- add reviewer queue visibility and decision workflows
- add token-backed auth and role-based access for contributor/reviewer flows
- add authenticated UI actions for contributor submissions and reviewer decisions
- add richer review queue UX: filters, assignment, notes, and history
- add protected admin audit visibility for workflow and auth events
- add admin session inspection and revocation controls
