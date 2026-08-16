import json

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.database import SessionLocal
from app.db_models import ArticleRecord, ClaimCitationRecord, ClaimRecord
from app.main import (
    article_jsonld,
    article_claims,
    claim_detail,
    entity_graph,
    export_knowledge,
    get_entities,
)
from app.seed import seed_claims_and_entities
from app.trust import detect_and_store_contradictions


def seeded_session():
    session = SessionLocal()
    seed_claims_and_entities(session)
    return session


def test_article_claims_quantum_computing_returns_seeded_claims() -> None:
    session = seeded_session()
    claims = article_claims("quantum-computing", session)
    assert len(claims) == 3
    assert [c.confidence for c in claims] == [0.85, 0.95, 0.95]
    assert [c.section_key for c in claims] == ["overview", "overview", "practical-constraints"]
    assert all(c.article_slug == "quantum-computing" for c in claims)
    session.close()


def test_article_claims_inflation_in_brazil_returns_seeded_claims() -> None:
    session = seeded_session()
    claims = article_claims("inflation-in-brazil", session)
    assert len(claims) == 3
    assert [c.confidence for c in claims] == [0.85, 0.95, 0.85]
    assert [c.section_key for c in claims] == [
        "historical-context",
        "historical-context",
        "current-drivers",
    ]
    session.close()


def test_article_claims_citations_have_non_empty_evidence_span() -> None:
    session = seeded_session()
    claim = article_claims("quantum-computing", session)[0]
    assert {c.source_id for c in claim.citations} == {"src-nist", "src-ibm"}
    assert all(c.evidence_span for c in claim.citations)
    assert "qubits" in claim.citations[0].evidence_span.lower()
    session.close()


def test_article_claims_unknown_slug_raises_404() -> None:
    session = seeded_session()
    with pytest.raises(HTTPException) as exc:
        article_claims("does-not-exist", session)
    assert exc.value.status_code == 404
    session.close()


def test_article_claims_returns_empty_list_without_seeding_claims() -> None:
    session = SessionLocal()
    claims = article_claims("quantum-computing", session)
    assert claims == []
    session.close()


def test_claim_detail_returns_claim_with_citation_chain_and_metrics() -> None:
    session = seeded_session()
    claims = article_claims("inflation-in-brazil", session)
    claim = claim_detail(claims[0].id, session)
    assert claim.article_slug == "inflation-in-brazil"
    assert claim.confidence == 0.85
    assert {c.source_id for c in claim.citations} == {"src-bcb", "src-imf"}
    assert all(c.evidence_span for c in claim.citations)
    assert claim.confidence_metrics is not None
    assert claim.confidence_metrics.overall_score == 0.85
    assert claim.confidence_metrics.source_quality_score == 0.85
    assert claim.confidence_metrics.cross_source_agreement_score == 1.0
    assert claim.confidence_metrics.freshness_score == 1.0
    assert claim.confidence_metrics.coverage_score == 1.0
    assert claim.confidence_metrics.human_review_score == 1.0
    assert claim.contradictions == []
    session.close()


def test_claim_detail_unknown_id_raises_404() -> None:
    session = seeded_session()
    with pytest.raises(HTTPException) as exc:
        claim_detail("does-not-exist", session)
    assert exc.value.status_code == 404
    session.close()


def test_seeded_claims_have_empty_contradictions() -> None:
    session = seeded_session()
    claims = article_claims("quantum-computing", session) + article_claims("inflation-in-brazil", session)
    assert all(c.contradictions == [] for c in claims)
    session.close()


def test_detect_and_store_contradictions_flags_negated_same_article_claim() -> None:
    session = seeded_session()
    article = session.scalars(select(ArticleRecord).where(ArticleRecord.slug == "inflation-in-brazil")).one()
    original = article_claims("inflation-in-brazil", session)[0]
    conflicting = ClaimRecord(
        article_id=article.id,
        claim_text="Brazil never experienced prolonged inflation instability before the Real Plan.",
        claim_type="historical",
        section_key="historical-context",
        status="active",
        confidence=0.0,
    )
    session.add(conflicting)
    session.flush()
    session.add(
        ClaimCitationRecord(
            claim_id=conflicting.id,
            source_id="src-bcb",
            evidence_span=conflicting.claim_text,
            support_type="supports",
        )
    )
    session.flush()
    detect_and_store_contradictions(session, conflicting)
    session.commit()
    session.expire_all()

    claim = claim_detail(conflicting.id, session)
    assert len(claim.contradictions) == 1
    contradiction = claim.contradictions[0]
    assert contradiction.contradiction_type == "claim_conflict"
    assert contradiction.severity == "medium"
    assert contradiction.status == "open"
    assert contradiction.source_id == "src-bcb"
    assert json.loads(contradiction.details_json)["conflicting_claim_id"] == original.id
    session.close()


def test_detect_and_store_contradictions_flags_contradicts_citation() -> None:
    session = seeded_session()
    article = session.scalars(select(ArticleRecord).where(ArticleRecord.slug == "quantum-computing")).one()
    claim = ClaimRecord(
        article_id=article.id,
        claim_text="Useful quantum computers are already widely deployed.",
        claim_type="factual",
        section_key="practical-constraints",
        status="active",
        confidence=0.0,
    )
    session.add(claim)
    session.flush()
    session.add(
        ClaimCitationRecord(
            claim_id=claim.id,
            source_id="src-nature",
            evidence_span=claim.claim_text,
            support_type="contradicts",
        )
    )
    session.flush()
    detect_and_store_contradictions(session, claim)
    session.commit()
    session.expire_all()

    hydrated = claim_detail(claim.id, session)
    assert [c.contradiction_type for c in hydrated.contradictions] == ["source_conflict"]
    assert hydrated.contradictions[0].source_id == "src-nature"
    session.close()


def test_get_entities_returns_all_entities_ordered_by_name() -> None:
    session = seeded_session()
    entities = get_entities(session)
    assert [e.name for e in entities] == [
        "Algorithms",
        "Brazilian Economy",
        "Central Banking",
        "Consumer Prices",
        "Cryptography",
        "Inflation",
        "Quantum Computing",
        "Quantum Mechanics",
    ]
    session.close()


def test_get_entities_returns_empty_list_when_unseeded() -> None:
    session = SessionLocal()
    entities = get_entities(session)
    assert entities == []
    session.close()


def test_entity_graph_quantum_computing_includes_outgoing_relationships_and_article_slug() -> None:
    session = seeded_session()
    graph = entity_graph("quantum-computing", session)
    assert graph.entity.name == "Quantum Computing"
    relationships = {(r.predicate, r.object_slug): r.confidence for r in graph.relationships}
    assert relationships == {
        ("is_application_of", "quantum-mechanics"): 1.0,
        ("threatens", "cryptography"): 0.90,
        ("uses", "algorithms"): 1.0,
    }
    assert graph.article_slugs == ["quantum-computing"]
    session.close()


def test_entity_graph_inflation_includes_outgoing_and_incoming_relationships() -> None:
    session = seeded_session()
    graph = entity_graph("inflation", session)
    relationships = {(r.subject_slug, r.predicate, r.object_slug): r.confidence for r in graph.relationships}
    assert relationships == {
        ("inflation", "measured_by", "consumer-prices"): 0.95,
        ("inflation", "affects", "brazilian-economy"): 0.90,
        ("central-banking", "targets", "inflation"): 1.0,
    }
    assert graph.article_slugs == ["inflation-in-brazil"]
    session.close()


def test_entity_graph_quantum_mechanics_includes_incoming_relationship() -> None:
    session = seeded_session()
    graph = entity_graph("quantum-mechanics", session)
    assert graph.entity.canonical_slug == "quantum-mechanics"
    assert [(r.subject_slug, r.predicate, r.object_slug) for r in graph.relationships] == [
        ("quantum-computing", "is_application_of", "quantum-mechanics"),
    ]
    assert graph.article_slugs == ["quantum-computing"]
    session.close()


def test_entity_graph_unknown_slug_raises_404() -> None:
    session = seeded_session()
    with pytest.raises(HTTPException) as exc:
        entity_graph("does-not-exist", session)
    assert exc.value.status_code == 404
    session.close()


def test_article_jsonld_uses_ld_json_content_type() -> None:
    session = seeded_session()
    response = article_jsonld("quantum-computing", session)
    assert response.status_code == 200
    assert response.media_type == "application/ld+json"
    body = json.loads(response.body)
    assert body["@context"] == "https://schema.org"
    assert body["@type"] == "Article"
    session.close()


def test_export_jsonld_uses_ld_json_content_type() -> None:
    session = seeded_session()
    response = export_knowledge("jsonld", session, limit=2, offset=0)
    assert response.status_code == 200
    assert response.media_type == "application/ld+json"
    assert int(response.headers["X-Total-Count"]) > 2
    assert 'rel="next"' in response.headers["Link"]
    body = json.loads(response.body)
    assert body["@context"] == "https://schema.org"
    assert len(body["@graph"]) == 2
    session.close()
