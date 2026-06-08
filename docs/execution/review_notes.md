# Review Notes

## Outcome

The repository now contains both the WikiAI blueprint and a working MVP scaffold.

This should be classified as:

- `MVP`: yes
- `Production-ready v1`: no

## Residual Gaps

- backend now persists article and suggestion data through SQLAlchemy, but defaults to SQLite unless `WIKIAI_DATABASE_URL` is set
- no real source ingestion, verification workers, or expert review workflow is implemented yet
- search is lexical/in-memory rather than OpenSearch-backed
- article chat is grounded to local seeded content, not a full RAG pipeline
- demo auth and role checks now exist, but they rely on seeded accounts rather than a production identity system
- the new admin surface is an MVP audit/activity dashboard, not a full moderation or user-management console
- contributor and reviewer UI actions now exist, but there are still no optimistic updates or robust inline validation/error states
- review history is visible, but there is still no richer audit explorer with pagination/export or reviewer workload management yet
- admin can revoke sessions, but there is still no broader account lifecycle management or permission editing

## Recommended Next Step

Build the next implementation slice on top of this MVP:

- replace seeded repositories with SQLAlchemy or equivalent persistence
- add migrations and production seed scripts
- implement revision submission APIs and richer queue prioritization rules
- replace seeded demo auth with a production identity flow
- add richer review UX such as assignment rules, reviewer notes editing, and a dedicated audit history explorer
- expand the admin surface into user management, moderation, and deeper audit navigation
- add real verification-job orchestration and source ingestion
