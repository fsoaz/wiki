# WikiAI Roadmap and Strategy

## Delivery Strategy

WikiAI should launch narrowly and credibly. The first milestone is not "cover everything"; it is "prove that AI-assisted knowledge can be trusted."

## MVP Roadmap: Shipped

### Shipped

- homepage, article page, and AI search UX
- article, revision, source, citation, and verification data model
- contributor suggestion and source submission workflow
- reviewer approval queue with filters, self-assignment, notes, and decision history
- contributor dashboard and admin audit log
- demo auth with role-based access (contributor, reviewer, admin)
- admin session inspection and revocation

### Shipped: epistemic database layer (2026-06-13)

The core architectural shift: the database is the product, the website is one view into it.

- atomic `claims` layer: each claim is an addressable object with `claim_type`, `status`, `confidence`, and citation chain
- knowledge graph: `entities` with typed `entity_relationships` and `article_entities` linkage
- machine-readable API endpoints: claims, claim detail, entity list, entity graph
- JSON-LD export: per-article Schema.org and full `@graph` bulk export
- `Database-first` established as first core principle in product spec

### Scope constraints

- English only in first release
- auto-publication limited to low-risk updates
- claim extraction is seeded by hand; AI extraction pipeline is v1 scope

### Success criteria (verified)

- every published article exposes citations, confidence, and last verification date
- every claim is addressable and returns its citation chain via API
- knowledge graph is traversable via entity relationship endpoints
- full knowledge graph is machine-exportable as JSON-LD

## Version 1 Roadmap: 90 Days

### Epistemic database depth

- AI claim extraction pipeline: automatically extract atomic claims from article section text
- evidence span population: store exact quoted passage from source document in `claim_citations.evidence_span`
- claim-level confidence computation: derive from source quality, cross-source agreement, freshness, and human review; persist to `confidence_metrics`
- contradiction detection: when a claim is added or updated, check for conflicts with existing claims on the same topic
- incoming entity relationship traversal in entity graph endpoint

### Product expansion

- article timelines
- section-level article assistant
- contributor reputation system
- expert verification onboarding
- admin moderation console

### Verification expansion

- source freshness monitoring
- automatic re-verification jobs
- revision proposal generation from monitored source changes

### Platform expansion

- hybrid search with vector retrieval at article-section and source-passage level
- analytics for trust, review throughput, and answer quality
- model and prompt registry
- `application/ld+json` content-type on JSON-LD endpoints

### Success criteria

- every claim has a non-empty `evidence_span` linking to source text
- confidence scores are computed, not hand-set
- contradiction detection flags conflicting claims before publication
- measurable confidence calibration against expert review

## Long-Term Roadmap: 12 Months

### Product

- multilingual support
- article comparison views
- embeddable verified answer widgets
- saved research workspaces for paid users

### Platform

- SPARQL or GraphQL query interface over the knowledge graph
- institution-facing tenant capabilities
- broader source connector network
- public trust and evidence API with rate-limited open access

### AI and trust

- domain-tuned verification models
- benchmark suite for hallucination, grounding, and contradiction handling
- richer claim lineage across revisions

## Monetization Strategy

### Free tier

- public reading
- core search
- article assistant with usage limits

### Pro subscription

- deeper research workflows
- advanced comparisons and exports
- saved collections and answer histories
- higher usage limits

### Institutional plans

- school and university accounts
- admin analytics
- custom trusted collections
- API access and governance controls

### Platform revenue

- licensing verified answer APIs
- evidence graph access
- trust metadata for partners and publishers

## Growth Strategy

- SEO through canonical, citation-rich topic pages
- shareable answer cards and timelines
- academic and library partnerships
- expert network programs with visible credentials
- focus initial acquisition on trust-sensitive domains

## Competitive Strategy

### Against traditional encyclopedias

- faster updates
- conversational explanation
- visible confidence and evidence graph

### Against search engines and answer engines

- canonical article ownership instead of response-only aggregation
- stronger attribution and reasoning transparency
- better handling of uncertainty and contradiction

### Against generic AI assistants

- hard grounding in approved evidence
- revision history and provenance
- human-governed publication model
