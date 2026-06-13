import uuid
from datetime import UTC, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class ArticleRecord(Base):
    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="published")
    verification_status: Mapped[str] = mapped_column(String(50), default="verified")
    current_confidence_score: Mapped[float] = mapped_column(Float)
    last_verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revision_count: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    sections: Mapped[list["ArticleSectionRecord"]] = relationship(
        back_populates="article", cascade="all, delete-orphan", order_by="ArticleSectionRecord.position"
    )
    timeline_events: Mapped[list["ArticleTimelineRecord"]] = relationship(
        back_populates="article", cascade="all, delete-orphan", order_by="ArticleTimelineRecord.position"
    )
    related_topics: Mapped[list["ArticleRelatedTopicRecord"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )
    sources: Mapped[list["SourceRecord"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )
    suggestions: Mapped[list["ArticleSuggestionRecord"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )
    source_submissions: Mapped[list["ArticleSourceSubmissionRecord"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )
    claims: Mapped[list["ClaimRecord"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )
    article_entities: Mapped[list["ArticleEntityRecord"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )


class ArticleSectionRecord(Base):
    __tablename__ = "article_sections"
    __table_args__ = (UniqueConstraint("article_id", "position"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id: Mapped[str] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    heading: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    citations_raw: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer)

    article: Mapped[ArticleRecord] = relationship(back_populates="sections")


class ArticleTimelineRecord(Base):
    __tablename__ = "article_timelines"
    __table_args__ = (UniqueConstraint("article_id", "position"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id: Mapped[str] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    event_date: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer)

    article: Mapped[ArticleRecord] = relationship(back_populates="timeline_events")


class ArticleRelatedTopicRecord(Base):
    __tablename__ = "article_related_topics"
    __table_args__ = (UniqueConstraint("article_id", "topic"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id: Mapped[str] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    topic: Mapped[str] = mapped_column(String(255))

    article: Mapped[ArticleRecord] = relationship(back_populates="related_topics")


class SourceRecord(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    article_id: Mapped[str] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255))
    publisher: Mapped[str] = mapped_column(String(255))
    tier: Mapped[str] = mapped_column(String(1))
    url: Mapped[str] = mapped_column(Text)
    published_at: Mapped[datetime.date] = mapped_column(Date)

    article: Mapped[ArticleRecord] = relationship(back_populates="sources")


class ArticleSuggestionRecord(Base):
    __tablename__ = "article_suggestions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id: Mapped[str] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    contributor_name: Mapped[str] = mapped_column(String(255))
    contributor_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    suggestion_type: Mapped[str] = mapped_column(String(50))
    summary: Mapped[str] = mapped_column(Text)
    proposed_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    article: Mapped[ArticleRecord] = relationship(back_populates="suggestions")


class ArticleSourceSubmissionRecord(Base):
    __tablename__ = "article_source_submissions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id: Mapped[str] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    contributor_name: Mapped[str] = mapped_column(String(255))
    contributor_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    publisher: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(Text)
    rationale: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    article: Mapped[ArticleRecord] = relationship(back_populates="source_submissions")


class ReviewQueueItemRecord(Base):
    __tablename__ = "review_queue_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id: Mapped[str] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    subject_type: Mapped[str] = mapped_column(String(50))
    subject_id: Mapped[str] = mapped_column(String(36), index=True)
    priority: Mapped[str] = mapped_column(String(50), default="normal")
    status: Mapped[str] = mapped_column(String(50), default="pending")
    assigned_reviewer_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    article: Mapped[ArticleRecord] = relationship()
    decisions: Mapped[list["ReviewDecisionRecord"]] = relationship(
        back_populates="queue_item", cascade="all, delete-orphan"
    )


class ReviewDecisionRecord(Base):
    __tablename__ = "review_decisions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    queue_item_id: Mapped[str] = mapped_column(ForeignKey("review_queue_items.id", ondelete="CASCADE"), index=True)
    reviewer_email: Mapped[str] = mapped_column(String(255))
    decision: Mapped[str] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    queue_item: Mapped[ReviewQueueItemRecord] = relationship(back_populates="decisions")


class UserRecord(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="active")
    auth_provider: Mapped[str] = mapped_column(String(50), default="demo")
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reputation_score: Mapped[float] = mapped_column(Float, default=0)
    locale: Mapped[str] = mapped_column(String(20), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    sessions: Mapped[list["SessionTokenRecord"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class SessionTokenRecord(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    user: Mapped[UserRecord] = relationship(back_populates="sessions")


class AuditLogRecord(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    actor_role: Mapped[str | None] = mapped_column(String(50), nullable=True)
    action: Mapped[str] = mapped_column(String(100))
    subject_type: Mapped[str] = mapped_column(String(100))
    subject_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    details_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class ClaimRecord(Base):
    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id: Mapped[str] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    claim_text: Mapped[str] = mapped_column(Text)
    claim_type: Mapped[str] = mapped_column(String(50))
    section_key: Mapped[str] = mapped_column(String(255))
    claim_hash: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(50), default="active")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    article: Mapped["ArticleRecord"] = relationship(back_populates="claims")
    citations: Mapped[list["ClaimCitationRecord"]] = relationship(
        back_populates="claim", cascade="all, delete-orphan"
    )


class ClaimCitationRecord(Base):
    __tablename__ = "claim_citations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id: Mapped[str] = mapped_column(ForeignKey("claims.id", ondelete="CASCADE"), index=True)
    source_id: Mapped[str] = mapped_column(String(64), index=True)
    evidence_span: Mapped[str] = mapped_column(Text, default="")
    support_type: Mapped[str] = mapped_column(String(50), default="supports")

    claim: Mapped["ClaimRecord"] = relationship(back_populates="citations")


class EntityRecord(Base):
    __tablename__ = "entities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255))
    entity_type: Mapped[str] = mapped_column(String(50))
    canonical_slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    article_entities: Mapped[list["ArticleEntityRecord"]] = relationship(
        back_populates="entity", cascade="all, delete-orphan"
    )
    outgoing_relationships: Mapped[list["EntityRelationshipRecord"]] = relationship(
        back_populates="subject_entity",
        foreign_keys="EntityRelationshipRecord.subject_entity_id",
        cascade="all, delete-orphan",
    )


class EntityRelationshipRecord(Base):
    __tablename__ = "entity_relationships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_entity_id: Mapped[str] = mapped_column(ForeignKey("entities.id", ondelete="CASCADE"), index=True)
    predicate: Mapped[str] = mapped_column(String(100))
    object_entity_id: Mapped[str] = mapped_column(ForeignKey("entities.id", ondelete="CASCADE"), index=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    source_claim_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    subject_entity: Mapped["EntityRecord"] = relationship(
        back_populates="outgoing_relationships",
        foreign_keys=[subject_entity_id],
    )
    object_entity: Mapped["EntityRecord"] = relationship(
        foreign_keys=[object_entity_id],
    )


class ArticleEntityRecord(Base):
    __tablename__ = "article_entities"

    article_id: Mapped[str] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    entity_id: Mapped[str] = mapped_column(ForeignKey("entities.id", ondelete="CASCADE"), primary_key=True)

    article: Mapped["ArticleRecord"] = relationship(back_populates="article_entities")
    entity: Mapped["EntityRecord"] = relationship(back_populates="article_entities")
