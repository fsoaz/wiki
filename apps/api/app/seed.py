from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .data import ARTICLES
from .db_models import (
    ArticleRecord,
    ArticleRelatedTopicRecord,
    ArticleSectionRecord,
    ArticleTimelineRecord,
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
