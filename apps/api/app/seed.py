from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .data import ARTICLES
from .db_models import (
    ArticleEntityRecord,
    ArticleRecord,
    ArticleRelatedTopicRecord,
    ArticleSectionRecord,
    ArticleTimelineRecord,
    ClaimCitationRecord,
    ClaimRecord,
    EntityRecord,
    EntityRelationshipRecord,
    SourceRecord,
    UserRecord,
)


def seed_articles(session: Session) -> None:
    has_articles = session.scalar(select(ArticleRecord.id).limit(1))
    if has_articles:
        return

    for article in ARTICLES:
        article_record = ArticleRecord(
            slug=article.slug,
            title=article.title,
            summary=article.summary,
            status="published",
            verification_status=article.verification_status,
            current_confidence_score=article.confidence_score,
            last_verified_at=datetime.fromisoformat(f"{article.last_verified_at}T00:00:00").replace(tzinfo=UTC),
            revision_count=article.revision_count,
        )
        session.add(article_record)
        session.flush()

        for index, section in enumerate(article.sections):
            session.add(
                ArticleSectionRecord(
                    article_id=article_record.id,
                    heading=section.heading,
                    content=section.content,
                    citations_raw="|".join(section.citations),
                    position=index,
                )
            )

        for index, timeline_event in enumerate(article.timeline):
            session.add(
                ArticleTimelineRecord(
                    article_id=article_record.id,
                    event_date=timeline_event.date,
                    title=timeline_event.title,
                    description=timeline_event.description,
                    position=index,
                )
            )

        for topic in article.related_topics:
            session.add(ArticleRelatedTopicRecord(article_id=article_record.id, topic=topic))

        for source in article.sources:
            session.add(
                SourceRecord(
                    id=source.id,
                    article_id=article_record.id,
                    title=source.title,
                    publisher=source.publisher,
                    tier=source.tier,
                    url=source.url,
                    published_at=source.published_at,
                )
            )

    session.commit()


def seed_users(session: Session) -> None:
    has_users = session.scalar(select(UserRecord.id).limit(1))
    if has_users:
        return

    session.add_all(
        [
            UserRecord(email="contributor@example.com", display_name="Demo Contributor", role="contributor"),
            UserRecord(email="reviewer@example.com", display_name="Demo Reviewer", role="reviewer"),
            UserRecord(email="admin@example.com", display_name="Demo Admin", role="admin"),
        ]
    )
    session.commit()


_CLAIMS_SEED: dict[str, list[dict]] = {
    "quantum-computing": [
        {
            "claim_text": "Quantum computers represent information with qubits rather than bits.",
            "claim_type": "factual",
            "section_key": "overview",
            "confidence": 0.95,
            "source_ids": ["src-nist", "src-ibm"],
        },
        {
            "claim_text": "A qubit can be prepared in a superposition, and quantum algorithms exploit interference patterns to amplify useful outcomes.",
            "claim_type": "factual",
            "section_key": "overview",
            "confidence": 0.95,
            "source_ids": ["src-nist"],
        },
        {
            "claim_text": "Useful quantum computation remains limited by decoherence, gate fidelity, error-correction overhead, and the difficulty of scaling hardware.",
            "claim_type": "factual",
            "section_key": "practical-constraints",
            "confidence": 0.92,
            "source_ids": ["src-nature", "src-nist"],
        },
    ],
    "inflation-in-brazil": [
        {
            "claim_text": "Brazil experienced prolonged inflation instability before the Real Plan.",
            "claim_type": "historical",
            "section_key": "historical-context",
            "confidence": 0.95,
            "source_ids": ["src-bcb", "src-imf"],
        },
        {
            "claim_text": "Inflation-targeting frameworks improved price stability in Brazil.",
            "claim_type": "factual",
            "section_key": "historical-context",
            "confidence": 0.88,
            "source_ids": ["src-bcb"],
        },
        {
            "claim_text": "Recent inflation trends often reflect food and energy prices, administered price changes, currency effects, and domestic policy choices.",
            "claim_type": "factual",
            "section_key": "current-drivers",
            "confidence": 0.85,
            "source_ids": ["src-bcb", "src-worldbank"],
        },
    ],
}

_ENTITIES_SEED: list[dict] = [
    {"name": "Quantum Computing", "entity_type": "technology", "canonical_slug": "quantum-computing", "description": "Computation using quantum mechanical phenomena such as superposition and entanglement."},
    {"name": "Quantum Mechanics", "entity_type": "field", "canonical_slug": "quantum-mechanics", "description": "Branch of physics governing behavior at atomic and subatomic scales."},
    {"name": "Cryptography", "entity_type": "field", "canonical_slug": "cryptography", "description": "Study and practice of secure communication techniques."},
    {"name": "Algorithms", "entity_type": "concept", "canonical_slug": "algorithms", "description": "Step-by-step computational procedures for solving problems."},
    {"name": "Inflation", "entity_type": "economic-concept", "canonical_slug": "inflation", "description": "Rate of increase in prices over a given period of time."},
    {"name": "Brazilian Economy", "entity_type": "economy", "canonical_slug": "brazilian-economy", "description": "The national economy of Brazil, one of the largest emerging markets."},
    {"name": "Central Banking", "entity_type": "institution", "canonical_slug": "central-banking", "description": "Management of money supply and interest rates by a central monetary authority."},
    {"name": "Consumer Prices", "entity_type": "metric", "canonical_slug": "consumer-prices", "description": "Price levels of goods and services purchased by households, used to measure inflation."},
]

_RELATIONSHIPS_SEED: list[dict] = [
    {"subject": "quantum-computing", "predicate": "is_application_of", "object": "quantum-mechanics", "confidence": 1.0},
    {"subject": "quantum-computing", "predicate": "threatens", "object": "cryptography", "confidence": 0.90},
    {"subject": "quantum-computing", "predicate": "uses", "object": "algorithms", "confidence": 1.0},
    {"subject": "inflation", "predicate": "measured_by", "object": "consumer-prices", "confidence": 0.95},
    {"subject": "central-banking", "predicate": "targets", "object": "inflation", "confidence": 1.0},
    {"subject": "inflation", "predicate": "affects", "object": "brazilian-economy", "confidence": 0.90},
]

_ARTICLE_ENTITIES_SEED: dict[str, list[str]] = {
    "quantum-computing": ["quantum-computing", "quantum-mechanics", "cryptography", "algorithms"],
    "inflation-in-brazil": ["inflation", "brazilian-economy", "central-banking", "consumer-prices"],
}


def seed_claims_and_entities(session: Session) -> None:
    has_entities = session.scalar(select(EntityRecord.id).limit(1))
    if has_entities:
        return

    slug_to_entity_id: dict[str, str] = {}
    for e in _ENTITIES_SEED:
        record = EntityRecord(
            name=e["name"],
            entity_type=e["entity_type"],
            canonical_slug=e["canonical_slug"],
            description=e["description"],
        )
        session.add(record)
        session.flush()
        slug_to_entity_id[e["canonical_slug"]] = record.id

    for rel in _RELATIONSHIPS_SEED:
        subject_id = slug_to_entity_id.get(rel["subject"])
        object_id = slug_to_entity_id.get(rel["object"])
        if subject_id and object_id:
            session.add(
                EntityRelationshipRecord(
                    subject_entity_id=subject_id,
                    predicate=rel["predicate"],
                    object_entity_id=object_id,
                    confidence=rel["confidence"],
                )
            )

    for article_slug, entity_slugs in _ARTICLE_ENTITIES_SEED.items():
        article = session.scalar(select(ArticleRecord).where(ArticleRecord.slug == article_slug))
        if article is None:
            continue
        for entity_slug in entity_slugs:
            entity_id = slug_to_entity_id.get(entity_slug)
            if entity_id:
                session.add(ArticleEntityRecord(article_id=article.id, entity_id=entity_id))

        for claim_data in _CLAIMS_SEED.get(article_slug, []):
            claim = ClaimRecord(
                article_id=article.id,
                claim_text=claim_data["claim_text"],
                claim_type=claim_data["claim_type"],
                section_key=claim_data["section_key"],
                status="active",
                confidence=claim_data["confidence"],
            )
            session.add(claim)
            session.flush()
            for source_id in claim_data["source_ids"]:
                session.add(ClaimCitationRecord(claim_id=claim.id, source_id=source_id, support_type="supports"))

    session.commit()
