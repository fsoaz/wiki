# WikiAI Product Specification

## Mission

WikiAI exists to become the most trusted source of knowledge on the internet by combining encyclopedia-grade structure with AI-assisted research, explanation, and continuous verification.

## Product Status

WikiAI is currently implemented as a functional MVP scaffold.

- The current build proves the end-to-end product loop: read, search, contribute, review, audit, and basic role-gated governance.
- The current build does not represent a production launch candidate.
- The current build should be treated as an MVP validation platform for workflow, interface, and domain model decisions.

## Product Positioning

WikiAI should sit between a traditional encyclopedia and a modern answer engine:

- From Wikipedia, it inherits structured canonical articles, revision history, and topic depth.
- From Notion, it inherits clean information architecture and modular content presentation.
- From Perplexity and ChatGPT, it inherits natural-language search, summaries, and conversational explanation.
- From scientific and institutional knowledge systems, it inherits explicit evidence handling and trust scoring.

The product must optimize for trust before engagement. AI should accelerate knowledge production and interpretation, but not obscure evidence or replace accountability.

## Core Principles

- `Verifiable`: every meaningful claim maps to supporting evidence.
- `Transparent`: confidence, sources, and reasoning traces are visible.
- `Continuously updated`: articles are monitored and re-verified over time.
- `Human accountable`: experts and moderators remain in the approval loop.
- `Structured`: articles are navigable, comparable, and machine-usable.

## Primary Audience

The first release targets public knowledge users who need high-quality answers for learning, research, and everyday decision support.

Secondary audiences:

- students and educators
- journalists and researchers
- knowledge workers
- institutional partners that need trusted explainable knowledge

## User Roles

### Visitor

- search and read articles
- ask grounded questions
- inspect citations, revisions, and confidence metadata

### Contributor

- suggest edits
- submit sources
- propose updates to outdated sections

### Verified Expert

- review evidence-backed revisions
- approve or reject claims and article updates
- validate domain-sensitive topics

### Administrator

- manage users, permissions, and moderation
- govern source policies and review workflows
- inspect audit logs and system health
- use the MVP admin dashboard to inspect recent workflow and auth events
- inspect and revoke active demo sessions in the MVP

## Core Product Surfaces

### Homepage

Purpose:
- establish trust quickly
- drive search-led discovery
- explain why WikiAI is different

Key modules:
- natural-language search bar
- featured verified topics
- recently updated articles
- methodology and source standards

### Intelligent Article Page

Each article should contain:

- title and canonical slug
- executive summary generated from approved evidence
- structured sections with inline citations
- timeline of relevant events
- related concepts and topics
- source table with tier metadata
- confidence score and confidence breakdown
- last verification date
- full revision history and diffs

### AI Search Experience

Search should support natural-language questions such as:

- "Explain quantum computing for beginners."
- "Compare Tesla and BYD."
- "Show the history of inflation in Brazil."

Outputs should include:

- direct grounded answer
- top matching articles
- supporting citations
- confidence and freshness signals
- follow-up questions

### Conversational Article Assistant

The assistant inside an article should:

- answer topic-specific questions
- summarize sections
- adapt explanations for beginner or advanced readers
- generate examples and analogies
- refuse to answer beyond the validated evidence set

### Contributor Workspace

The contributor experience should include:

- source submission
- structured edit suggestions
- reputation and acceptance history
- recommendations for missing-citation or outdated topics
- authenticated submission directly from article pages in the MVP

### Verification Workspace

The reviewer experience should include:

- prioritized queues
- article diffs
- extracted claims
- supporting and contradicting evidence
- confidence changes
- approval and escalation actions
- authenticated approve/reject controls in the MVP review dashboard
- queue filters, self-assignment, and visible decision history in the MVP

## Source Credibility Framework

### Tier A

- peer-reviewed scientific publications
- universities and academic institutions
- government agencies

### Tier B

- recognized research organizations
- industry associations
- international institutions

### Tier C

- reputable news organizations

### Tier D

- expert blogs and secondary sources

Default policy:

- Tier A and B should be preferred for stable factual claims.
- Tier C can support current events, context, and synthesis when clearly dated.
- Tier D must not be the sole support for critical claims.

## Trust Features

Every article and AI answer should expose:

- sources used
- evidence links
- confidence score
- verification status
- last verification date
- revision history
- explanation of how conclusions were formed

## Editorial Model

WikiAI uses an AI-assisted but human-governed model:

- AI discovers sources, drafts summaries, extracts claims, and proposes revisions.
- Contributors widen coverage and flag problems.
- Verified experts validate high-impact changes.
- Administrators manage policy, abuse, and workflow integrity.

## Current MVP State

The current MVP supports a narrow but end-to-end governance loop:

- demo sign-in with seeded contributor, reviewer, and admin roles
- contributor suggestions and source submissions from article pages
- durable review queue creation for every submission
- reviewer approval and rejection from the dashboard
- reviewer self-assignment, filtering, notes, and decision history
- contributor visibility into submission status
- admin visibility into recent audit events and queue/system activity
- admin inspection and revocation of active sessions

The current MVP is intentionally limited:

- demo auth instead of production identity
- SQLite-by-default local persistence model
- no real source-ingestion or verification-agent runtime
- no OpenSearch/vector retrieval stack
- no production-grade moderation, observability, or deployment controls

## Success Metrics

### Trust metrics

- citation coverage per article
- percent of claims with multi-source support
- confidence-score calibration against expert review
- time since last verification

### User metrics

- search success rate
- article completion rate
- follow-up question rate
- return visits

### Workflow metrics

- review turnaround time
- update proposal acceptance rate
- false positive rate for contradiction detection
- source freshness SLA compliance
