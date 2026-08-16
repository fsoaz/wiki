# Query claims and the knowledge graph

Read WikiAI as a database. These routes are public. You do not need a session.

Start the API first ([getting started](../tutorials/getting-started.md)). Seeded slugs include `quantum-computing` and `inflation-in-brazil`.

## List claims for an article

```bash
curl -s http://localhost:8000/api/v1/articles/quantum-computing/claims
```

Each item includes `claim_text`, `claim_type`, `section_key`, `status`, `confidence`, a `citations` array, a `confidence_metrics` breakdown (`source_quality_score`, `cross_source_agreement_score`, `freshness_score`, `coverage_score`, `human_review_score`), and a `contradictions` array.

Unknown slugs return `404` `Article not found`.

The website renders this same breakdown as a "Trust breakdown" panel on each article page — this endpoint is what feeds it.

## Fetch one claim

Copy a claim `id` from the list response, then:

```bash
curl -s http://localhost:8000/api/v1/claims/CLAIM_ID
```

Replace `CLAIM_ID` with the UUID from the previous response. Unknown ids return `404` `Claim not found`.

> **Note:** `citations[].evidence_span` is filled from the matching article section. Claim `confidence` is the weakest supporting source tier. See [current MVP](../reference/current-mvp.md).

## Walk the entity graph

List entities:

```bash
curl -s http://localhost:8000/api/v1/entities
```

Load one node and its **outgoing then incoming** relationships:

```bash
curl -s http://localhost:8000/api/v1/entities/quantum-computing
```

The payload includes the entity, typed `relationships` (`predicate`, `subject_slug`, `object_slug`, `object_name`, `confidence`), and `article_slugs`. Incoming edges are included after outgoing edges.

Unknown slugs return `404` `Entity not found`.

## Export JSON-LD

One article as Schema.org JSON-LD:

```bash
curl -s http://localhost:8000/api/v1/articles/quantum-computing/jsonld
```

Paginated graph export (default 100 records, maximum 500):

```bash
curl -s http://localhost:8000/api/v1/export?format=jsonld
```

`format` must be `jsonld`. The response `Content-Type` is `application/ld+json`.

## Next

- [API reference](../reference/api.md) for every route
- [Review a submission](review-a-submission.md) for the write path
