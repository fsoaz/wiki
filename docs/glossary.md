# Glossary

Terms used across WikiAI docs. Link here on first use in a page.

## Claim

An atomic, addressable statement extracted from an article. Each claim has a type (factual, historical, statistical, definitional, or comparative), a status (active, disputed, or deprecated), a confidence value, and a citation chain.

In the MVP, claims are hand-seeded. Claim `confidence` is computed from supporting source tiers. See [current MVP](reference/current-mvp.md).

## Confidence

A numeric score that should reflect how well sources support a claim or article. Article pages and search answers expose a confidence value.

In the MVP, article scores are seeded with the content. Claim scores are computed as the weakest supporting citation tier and returned with a `confidence_metrics` breakdown.

## Demo auth

Email-only sign-in against three seeded accounts. There is no password, MFA, or production identity provider. Sessions are bearer tokens stored in an HTTP-only cookie named `wikiai_token` on the frontend.

The API stores only a SHA-256 digest of each token, expires sessions after 12 hours, and keeps at most five per user. Those controls limit the damage from a leaked token. They do not make email-only login safe for real users. See [security](reference/security.md).

## Entity

A named node in the knowledge graph, such as a technology, field, concept, economy, institution, or metric. Entities have a stable human-readable `canonical_slug` and typed relationships to other entities.

## Epistemic database

The product thesis: WikiAI is a machine-readable knowledge store first and a website second. Articles, claims, citations, confidence, and entities are API resources. Any UI is one consumer of that API.

## Evidence span

The exact quoted passage from a source that supports a claim, stored on `claim_citations.evidence_span`.

In the MVP this field is populated from the matching article section text.

## Grounding

Restricting an AI answer to approved article content and linked sources. Search and article chat in the MVP answer from seeded article text. They are not a full retrieval-augmented generation (RAG) pipeline.

## JSON-LD

JSON for Linked Data. WikiAI can export an article as Schema.org JSON-LD and page through the graph as JSON-LD `@graph` responses. JSON-LD endpoints return `Content-Type: application/ld+json`.

## Review queue

Durable work items created when a contributor submits an article suggestion or a source. Reviewers filter the queue, assign items to themselves, and approve or reject with notes.

## Source tier

A credibility class for a source:

- **Tier A:** peer-reviewed scientific publications, universities, government agencies
- **Tier B:** recognized research organizations, industry associations, international institutions
- **Tier C:** reputable news organizations
- **Tier D:** expert blogs and secondary sources

Default policy: prefer A and B for stable factual claims. C can support current events when clearly dated. D must not be the sole support for critical claims.

## Verification

The process of checking claims against sources and recording a result. The product vision includes automated re-verification jobs. The MVP stores `last_verified_at` and `verification_status` on seeded articles. It does not run verification workers.
