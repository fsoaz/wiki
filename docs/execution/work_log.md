# Work Log

## 2026-06-13

- assessed gap between epistemic database vision and actual MVP implementation
- identified core misalignment: project was website-first; database served the website rather than being the product
- implemented atomic claims layer: `ClaimRecord`, `ClaimCitationRecord` ORM models and seed data
- implemented knowledge graph: `EntityRecord`, `EntityRelationshipRecord`, `ArticleEntityRecord` ORM models
- added 6 machine-readable API endpoints: claims list, claim detail, entity list, entity graph, article JSON-LD, full export
- seeded 6 atomic claims (3 per article) with citation links to source IDs and per-claim confidence scores
- seeded 8 entities and 6 typed relationships forming a traversable knowledge graph
- added Schema.org JSON-LD output for articles and full `@graph` bulk export
- updated `product.md` core principles: `Database-first` is now the first principle
- updated `architecture.md`: new "Knowledge Graph and Machine-Readable API" section with endpoint table
- updated FastAPI app description to reflect database-first positioning
- extended `001_init.sql` with `claim_citations`, `entities`, `entity_relationships`, `article_entities` tables

## 2026-06-07

- assessed repository state and confirmed it is a docs-first greenfield workspace
- converted the approved WikiAI plan into persistent product, architecture, and roadmap documents
- established baseline standards for APIs, AI behavior, testing, and documentation conventions
- replaced placeholder README content with a navigable repository overview
- scaffolded a monorepo MVP with `apps/web` and `apps/api`
- implemented seeded article read, search, and article-chat flows
- added a PostgreSQL initialization script covering the core WikiAI schema
- added local Docker and application manifests for frontend, backend, and database development
- installed frontend and backend dependencies and validated the scaffold with tests and a production web build
- refactored the API from in-memory article reads to SQLAlchemy-backed persistence
- added database bootstrap and startup seeding for canonical MVP articles
- added a durable `POST /api/v1/articles/{slug}/suggestions` endpoint for contributor inputs
- added isolated SQLite-backed API tests for persistence and suggestion creation
- added article suggestion listing and source submission APIs
- added contributor overview aggregation by contributor email
- added a frontend contributor dashboard route for submitted suggestions and sources
- added review queue records for suggestion and source-submission items
- added reviewer queue listing, overview, and decision APIs
- added a frontend reviewer dashboard route for pending, approved, and rejected queue visibility
- added seeded demo users, backend auth sessions, and API auth endpoints
- enforced contributor and reviewer role checks on protected mutation and dashboard APIs
- added a frontend sign-in route and cookie-backed protected dashboard access
- added contributor submission forms directly on article pages
- added inline approve and reject actions to the reviewer dashboard
- aligned repository docs with the now interactive end-to-end MVP workflow
- added reviewer queue filtering by status and subject type
- added self-assignment for queue items plus visible decision notes/history in the reviewer dashboard
- extended backend review queue responses to include decision history and assignment state
- added durable audit log records for auth, submission, assignment, and review decision events
- added protected admin overview and audit APIs
- added a frontend admin dashboard for recent audit and activity inspection
- added admin session listing and revocation APIs
- added admin UI controls for active session inspection and revocation
