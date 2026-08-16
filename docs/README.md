# WikiAI documentation

This index is the map of the docs. Start here if you are not sure which page to open.

Docs follow [Diátaxis](https://diataxis.fr/): tutorials teach, how-to guides solve a job, reference states facts, explanation gives context.

## Audience

| Label | Who | What they need |
| --- | --- | --- |
| Public | Developers consuming the API or running the MVP | Tutorials, how-to guides, API reference, glossary |
| Internal | Contributors, reviewers of this repo, coding agents | Standards, execution notes, contributing rules |

Execution notes are working memory, not a product contract. See [Archive policy](#archive-policy).

## Tutorials (learn)

| Page | Audience |
| --- | --- |
| [Get the MVP running](tutorials/getting-started.md) | Public |

## How-to guides (do a job)

| Page | Audience |
| --- | --- |
| [Use PostgreSQL locally](how-to/use-postgres.md) | Public |
| [Sign in and use roles](how-to/sign-in-and-roles.md) | Public |
| [Query claims and the knowledge graph](how-to/query-claims-and-graph.md) | Public |
| [Review a submission](how-to/review-a-submission.md) | Public |

## Reference (look up)

| Page | Audience |
| --- | --- |
| [API](reference/api.md) | Public |
| [Configuration](reference/configuration.md) | Public |
| [Current MVP](reference/current-mvp.md) | Public |
| [Security](reference/security.md) | Public |
| [Glossary](glossary.md) | Public |
| Generated OpenAPI UI at `http://localhost:8000/docs` | Public |

## Explanation (understand)

| Page | Audience |
| --- | --- |
| [Product](explanation/product.md) | Public |
| [Target architecture](explanation/architecture.md) | Public |
| [Roadmap](explanation/roadmap.md) | Public |

## Internal

| Page | Audience |
| --- | --- |
| [Documentation conventions](standards/conventions.md) | Internal |
| [API rules](standards/api_rules.md) | Internal |
| [AI agent rules](standards/ai_agent_rules.md) | Internal |
| [Testing standards](standards/testing.md) | Internal |
| [Current task](execution/current_task.md) | Internal |
| [Work log](execution/work_log.md) | Internal |
| [Review notes](execution/review_notes.md) | Internal |
| [Test evidence](execution/test_evidence.md) | Internal |

Hub files at the repository root: [README.md](../README.md), [CONTRIBUTING.md](../CONTRIBUTING.md), [CHANGELOG.md](../CHANGELOG.md), [AGENTS.md](../AGENTS.md).

## Archive policy

- `docs/execution/` is append-only working memory. It records what a session did. It is not the source of truth for product behavior.
- When a task finishes, move lasting facts into reference, explanation, or the changelog. Leave a short note in the work log.
- `docs/execution/current_task.md` is the live execution pointer. Stale claims belong in the work log, not in tutorials or the README.
- Do not publish placeholder text such as "TODO: fill this in later" in hub docs.
- When code changes, update the docs that describe it in the same pull request.
