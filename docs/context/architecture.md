# WikiAI System Architecture

## Architecture Summary

WikiAI is a public epistemic database first, a website second. The canonical data model — entities, claims, citations, confidence scores — is the product. The Next.js frontend is one consumer of the API; external machines and researchers are equally first-class consumers.

WikiAI should be built as a read-optimized, event-driven knowledge platform with explicit separation between canonical content, evidence, verification, and AI interaction layers.

Recommended stack:

- frontend: `Next.js`, `TypeScript`, `Tailwind CSS`, `shadcn/ui`
- backend: `FastAPI`
- database: `PostgreSQL`
- search: `OpenSearch`
- cache and queues: `Redis`
- orchestration: `Docker`, `Kubernetes`
- AI: LLMs, embeddings, RAG, and workflow agents

## Logical Architecture

```text
[Clients]
  |
  v
[CDN / Edge]
  |
  v
[Next.js Frontend]
  |
  v
[API Gateway / BFF]
  |
  +--> [Identity Service]
  +--> [Article Service]
  +--> [Search Service]
  +--> [Conversation Service]
  +--> [Workflow Service]
  |
  v
[Event Bus]
  |
  +--> [Source Ingestion Workers]
  +--> [Verification Workers]
  +--> [Indexing Workers]
  +--> [Notification Workers]
  |
  v
[PostgreSQL] [OpenSearch] [Redis] [Vector Store] [Object Storage]
  |
  v
[External Trusted Sources, Crawlers, APIs, LLM Providers]
```

## Service Boundaries

### Identity Service

- user accounts
- roles and permissions
- expert verification status
- sessions and MFA
- current MVP implementation uses seeded demo users plus token-backed API sessions
- current MVP admin APIs can inspect and revoke active auth sessions

### Article Service

- canonical article storage
- structured sections and timelines
- revision management
- publication states

### Source Service

- source metadata normalization
- source tiering
- provenance tracking
- archived source artifacts

### Citation Service

- claim-to-source mapping
- evidence span storage
- citation rendering data

### Verification Service

- claim extraction
- credibility scoring
- contradiction detection
- confidence calculation

### Search Service

- lexical retrieval
- semantic retrieval
- ranking and snippet generation
- search analytics

### Conversation Service

- grounded chat over articles
- answer trace generation
- citation attachment
- conversation policy enforcement

### Workflow Service

- contributor suggestions
- expert review queues
- SLA timers
- escalation rules
- current MVP includes queue creation for contributor submissions and reviewer approve/reject decisions
- current MVP also includes reviewer self-assignment, filterable queue reads, and stored decision notes

### Audit and Policy Service

- immutable audit events
- moderation actions
- model and prompt version records
- current MVP records auth, submission, assignment, and review decision events
- current MVP admin endpoints expose recent audit events and active session state

## Data Model

### Users and Governance

#### `users`

- `id`
- `email`
- `password_hash`
- `auth_provider`
- `display_name`
- `role`
- `reputation_score`
- `status`
- `locale`
- `created_at`

#### `user_profiles`

- `user_id`
- `bio`
- `expertise_areas`
- `verification_level`
- `organization`
- `country`

#### `expert_verifications`

- `id`
- `user_id`
- `credential_type`
- `issuer`
- `credential_reference`
- `status`
- `reviewed_by`
- `reviewed_at`

### Articles and Structure

#### `articles`

- `id`
- `slug`
- `title`
- `status`
- `primary_language`
- `current_revision_id`
- `canonical_summary_revision_id`
- `current_confidence_score`
- `last_verified_at`
- `created_by`
- `created_at`

#### `article_sections`

- `id`
- `article_id`
- `revision_id`
- `section_key`
- `heading`
- `content_md`
- `position`

#### `article_timelines`

- `id`
- `article_id`
- `revision_id`
- `event_date`
- `event_label`
- `event_description`
- `position`

#### `article_relationships`

- `id`
- `article_id`
- `related_article_id`
- `relationship_type`
- `strength_score`

#### `categories`

- `id`
- `name`
- `slug`
- `parent_id`

#### `article_categories`

- `article_id`
- `category_id`

#### `tags`

- `id`
- `label`
- `slug`

#### `article_tags`

- `article_id`
- `tag_id`

### Revisions, Claims, and Sources

#### `revisions`

- `id`
- `article_id`
- `revision_number`
- `author_type`
- `author_user_id`
- `source_revision_parent_id`
- `change_summary`
- `status`
- `published_at`
- `created_at`

#### `revision_diffs`

- `id`
- `revision_id`
- `diff_json`
- `rendered_diff_md`

#### `claims`

- `id`
- `article_id`
- `revision_id`
- `claim_text`
- `claim_type`
- `section_key`
- `claim_hash`
- `status`

#### `sources`

- `id`
- `source_type`
- `title`
- `publisher`
- `authors_json`
- `publication_date`
- `url`
- `doi`
- `language`
- `tier`
- `credibility_score`
- `freshness_score`
- `retrieved_at`

#### `source_artifacts`

- `id`
- `source_id`
- `artifact_type`
- `storage_uri`
- `checksum`
- `parsed_text_version`
- `extracted_metadata_json`

#### `citations`

- `id`
- `claim_id`
- `source_id`
- `evidence_span`
- `support_type`
- `weight`
- `created_at`

### Verification and Confidence

#### `verification_records`

- `id`
- `article_id`
- `revision_id`
- `verification_run_id`
- `result`
- `verified_at`
- `verified_by_type`
- `verified_by_user_id`

#### `contradictions`

- `id`
- `claim_id`
- `source_id`
- `contradiction_type`
- `severity`
- `details_json`
- `status`

#### `confidence_metrics`

- `id`
- `subject_type`
- `subject_id`
- `overall_score`
- `source_quality_score`
- `cross_source_agreement_score`
- `freshness_score`
- `coverage_score`
- `human_review_score`
- `computed_at`

### Conversations, Workflow, and Audit

#### `ai_conversations`

- `id`
- `user_id`
- `article_id`
- `query`
- `response_text`
- `grounding_status`
- `confidence_score`
- `created_at`

#### `ai_answer_citations`

- `id`
- `conversation_id`
- `claim_id`
- `source_id`
- `span_reference`
- `order_index`

#### `verification_jobs`

- `id`
- `subject_type`
- `subject_id`
- `trigger_type`
- `priority`
- `status`
- `started_at`
- `completed_at`

#### `review_queue_items`

- `id`
- `article_id`
- `subject_type`
- `subject_id`
- `priority`
- `status`
- `assigned_reviewer_email`
- `created_at`
- `updated_at`

#### `review_decisions`

- `id`
- `queue_item_id`
- `reviewer_email`
- `decision`
- `notes`
- `created_at`

#### `auth_sessions`

- `id`
- `user_id`
- `token`
- `created_at`

#### `audit_logs`

- `id`
- `actor_email`
- `actor_role`
- `action`
- `subject_type`
- `subject_id`
- `details_json`
- `created_at`

- `id`
- `actor_type`
- `actor_id`
- `action`
- `subject_type`
- `subject_id`
- `before_json`
- `after_json`
- `ip_hash`
- `created_at`

#### `moderation_events`

- `id`
- `target_type`
- `target_id`
- `policy_code`
- `action_taken`
- `reviewer_id`
- `created_at`

## Search and Retrieval Design

### OpenSearch indexes

- `articles_index` for title, summary, sections, categories, and quality signals
- `sources_index` for source metadata and parsed content
- `claims_index` for claim lookup and contradiction analysis

### Vector retrieval

Embed:

- article sections
- source passages
- claims
- approved answer contexts

Use hybrid retrieval:

- lexical search for precision and entity matching
- semantic search for natural-language understanding
- confidence and freshness features in final ranking

## AI Verification Pipeline

### Stage 1: source discovery

- pull from trusted feeds and APIs
- expand through search providers and crawlers
- deduplicate by canonical URL, DOI, and semantic similarity

### Stage 2: source credibility scoring

Score on:

- institution quality
- publisher trust class
- peer-review or official status
- historical reliability
- author authority
- freshness and update cadence

### Stage 3: claim extraction

- split article text into atomic claims
- classify claims as factual, historical, statistical, definitional, or comparative
- attach claim location and semantic fingerprint

### Stage 4: cross-source validation

- find supporting passages
- require independent corroboration for important claims
- detect thin sourcing and source circularity

### Stage 5: contradiction detection

- identify direct conflicts
- identify stale figures and date drift
- detect scope mismatch between sources and claims

### Stage 6: confidence scoring

Inputs:

- source quality
- source independence
- evidence count
- recency
- contradiction severity
- human review status

### Stage 7: human review workflow

Mandatory review for:

- controversial topics
- low-confidence changes
- high-traffic pages
- policy-sensitive edits

### Stage 8: publication approval

- auto-publish only low-risk, high-confidence updates
- otherwise route to expert or admin approval

## Article Creation Workflow

1. Topic is proposed by user, editor, or AI seed generation.
2. Research agent gathers candidate sources and topic clusters.
3. Outline agent builds section structure and timeline candidates.
4. Drafting agent generates article text with citation placeholders.
5. Verification pipeline validates claims and computes confidence.
6. Reviewers assess evidence, contradictions, and confidence shifts.
7. Approved revision becomes canonical.
8. Search, vector, and cache indexes refresh.
9. Monitoring is scheduled for new source changes.

## Knowledge Graph and Machine-Readable API

The epistemic database exposes knowledge as a graph of entities and typed relationships, not just prose articles. Key additions to the data model:

### `entities`

- `id`
- `name`
- `entity_type` (technology, field, concept, economy, institution, metric)
- `canonical_slug`
- `description`

### `entity_relationships`

- `id`
- `subject_entity_id`
- `predicate` (typed relationship: `is_application_of`, `threatens`, `uses`, `targets`, `measured_by`, `affects`)
- `object_entity_id`
- `confidence`
- `source_claim_id` (claim that supports this relationship)

### `article_entities`

Junction table linking articles to the entities they cover.

### `claims` (active in MVP)

- `id`
- `article_id`
- `claim_text` (atomic, one verifiable statement)
- `claim_type` (factual, historical, statistical, definitional, comparative)
- `section_key`
- `confidence`
- `status` (active, disputed, deprecated)

### `claim_citations`

- `id`
- `claim_id`
- `source_id`
- `evidence_span`
- `support_type` (supports, contradicts, contextualizes)

### Machine-Readable Endpoints (MVP)

| Endpoint | Output |
|----------|--------|
| `GET /api/v1/articles/{slug}/claims` | Atomic claims for an article with per-claim confidence and citations |
| `GET /api/v1/claims/{id}` | Single claim with full citation chain |
| `GET /api/v1/entities` | All entities in the knowledge graph |
| `GET /api/v1/entities/{slug}` | Entity + outgoing relationships + linked article slugs |
| `GET /api/v1/articles/{slug}/jsonld` | Article as Schema.org JSON-LD |
| `GET /api/v1/export?format=jsonld` | Full knowledge graph as JSON-LD `@graph` |

## Current MVP Interaction Layer

- article pages expose authenticated forms for improvement suggestions and source submissions
- every submission creates a durable review queue item
- reviewer dashboard exposes queue visibility plus approve/reject actions
- review queue supports status and subject-type filtering, self-assignment, and decision history
- contributor dashboard exposes submission status scoped to the authenticated user
- admin dashboard exposes aggregate counts and recent audit activity
- admin dashboard exposes active session inspection and revocation
- machine-readable API exposes claims, entities, relationships, and JSON-LD export without auth

## User Interface Wireframes

### Homepage

```text
+----------------------------------------------------------+
| Logo | Explore | Categories | Latest Verified | Sign In |
+----------------------------------------------------------+
| The most trusted AI-powered knowledge platform           |
| [ Ask WikiAI anything...                               ] |
| Popular prompts                                         |
+----------------------------------------------------------+
| Verified today | Citation density | Expert reviewed     |
+----------------------------------------------------------+
| Featured topics | Trending questions | Recent updates   |
+----------------------------------------------------------+
| How verification works | Source standards | API         |
+----------------------------------------------------------+
```

### Article page

```text
+-------------------------------------------------------------------+
| Breadcrumbs                                                       |
| Title                                                             |
| Confidence | Last verified | Revision | Tags                      |
+-------------------------------------------------------------------+
| Executive summary                                                 |
| [Ask this article] [View sources] [View history]                  |
+-------------------------------------------------------------------+
| Nav rail     | Main sections with inline citations | Trust rail   |
|              | Timeline                            | Sources mix   |
|              | Related concepts                    | Confidence    |
+-------------------------------------------------------------------+
| Full source table | Contradictions | Revision history | Suggestion |
+-------------------------------------------------------------------+
| Sticky article assistant                                          |
+-------------------------------------------------------------------+
```

### AI search experience

```text
+---------------------------------------------------------------+
| Search input                                                  |
| Tabs: Answer | Articles | Sources | Timelines                 |
+---------------------------------------------------------------+
| Cited answer                     | Matching articles          |
| Confidence and evidence trace    | Related entities           |
| Supporting sources               | Follow-up prompts          |
+---------------------------------------------------------------+
```

### Contributor dashboard

```text
+---------------------------------------------------------------+
| My suggestions | Submitted sources | Reputation               |
+---------------------------------------------------------------+
| Recommended tasks: outdated topics, missing citations         |
+---------------------------------------------------------------+
```

### Verification dashboard

```text
+---------------------------------------------------------------+
| Queues: High risk | Breaking updates | Low confidence         |
+---------------------------------------------------------------+
| Revision diff | Claims | Supporting evidence | Actions        |
+---------------------------------------------------------------+
```

### Admin panel

```text
+---------------------------------------------------------------+
| Users | Expert approvals | Moderation | Source policy         |
+---------------------------------------------------------------+
| Audit explorer | Model registry | Queue health | Abuse flags  |
+---------------------------------------------------------------+
```

## Security Architecture

- RBAC with least privilege and workflow-scoped permissions
- MFA for experts and administrators
- encryption in transit and at rest
- secret management in vault-backed infrastructure
- immutable audit trails for content and moderation events
- prompt and model version tracking for all AI-generated output
- rate limiting, bot detection, and abuse heuristics on public APIs
- source poisoning defense using reputation controls and anomaly scoring

## Scalability and Reliability

Design targets:

- 100M+ users
- millions of articles
- global low-latency read path
- near-real-time update propagation
- high availability under regional failure

Key strategies:

- global CDN for article reads
- regional API and search clusters
- PostgreSQL read replicas and partitioning
- asynchronous event-driven verification and indexing
- Redis for hot object caching and rate limiting
- queue-backed worker pools for ingestion and AI tasks
- graceful degradation to search results or cached article reads if LLM paths fail

Indicative objectives:

- article page p95 under 300 ms from cache-heavy traffic
- search answer p95 under 2.5 s
- 99.95% read availability
