# API Rules

- Public APIs must return evidence and trust metadata for any AI-generated answer.
- Article read APIs must expose `confidence_score`, `last_verified_at`, and revision identifiers.
- Search APIs must separate direct answers from supporting articles and sources.
- Mutation APIs must produce audit log events.
- Review and moderation APIs must enforce RBAC and actor attribution.
- AI-facing APIs must reject ungrounded answer publication.
- Prefer explicit versioning once external clients are introduced.
