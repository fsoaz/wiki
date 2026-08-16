from collections.abc import Iterable
from datetime import UTC, datetime, timedelta
import hashlib
import json
import re
import secrets

from sqlalchemy import Select, delete, or_, select, update
from sqlalchemy.orm import Session, selectinload
from .db_models import (
    ArticleEntityRecord,
    AuditLogRecord,
    ArticleRecord,
    ArticleSectionRecord,
    ArticleSourceSubmissionRecord,
    ArticleSuggestionRecord,
    ClaimCitationRecord,
    ClaimRecord,
    EntityRecord,
    EntityRelationshipRecord,
    ReviewDecisionRecord,
    ReviewQueueItemRecord,
    SessionTokenRecord,
    UserRecord,
)
from .config import settings
from .models import (
    AdminOverview,
    Article,
    ArticleSection,
    ArticleSuggestion,
    ArticleSuggestionCreate,
    AuditLogEntry,
    AuthSession,
    AuthUser,
    AuthLoginRequest,
    AuthSessionInfo,
    Claim,
    ClaimCitation,
    ConfidenceMetrics,
    Contradiction,
    ContributorOverview,
    Entity,
    EntityGraph,
    EntityRelationship,
    ReviewAssignment,
    ReviewDecision,
    ReviewDecisionCreate,
    ReviewerOverview,
    ReviewQueueItem,
    Source,
    SourceSubmission,
    SourceSubmissionCreate,
    TimelineEvent,
)


_EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def hydrate_article(record: ArticleRecord) -> Article:
    return Article(
        slug=record.slug,
        title=record.title,
        summary=record.summary,
        confidence_score=record.current_confidence_score,
        verification_status=record.verification_status,
        last_verified_at=record.last_verified_at.date(),
        related_topics=[topic.topic for topic in record.related_topics],
        sections=[
            ArticleSection(
                heading=section.heading,
                content=section.content,
                citations=section.citations_raw.split("|") if section.citations_raw else [],
            )
            for section in sorted(record.sections, key=lambda item: item.position)
        ],
        timeline=[
            TimelineEvent(
                date=event.event_date,
                title=event.title,
                description=event.description,
            )
            for event in sorted(record.timeline_events, key=lambda item: item.position)
        ],
        sources=[
            Source(
                id=source.id,
                title=source.title,
                publisher=source.publisher,
                tier=source.tier,
                url=source.url,
                published_at=source.published_at,
            )
            for source in record.sources
        ],
        revision_count=record.revision_count,
    )


def _article_query() -> Select[tuple[ArticleRecord]]:
    return select(ArticleRecord).options(
        selectinload(ArticleRecord.sections),
        selectinload(ArticleRecord.timeline_events),
        selectinload(ArticleRecord.related_topics),
        selectinload(ArticleRecord.sources),
    )


def list_articles(session: Session) -> list[Article]:
    records = session.scalars(_article_query().order_by(ArticleRecord.title.asc())).all()
    return [hydrate_article(record) for record in records]


def get_article_by_slug(session: Session, slug: str) -> Article | None:
    record = session.scalars(_article_query().where(ArticleRecord.slug == slug)).first()
    return hydrate_article(record) if record else None


def search_articles(session: Session, query: str) -> Iterable[Article]:
    normalized = query.lower().strip()
    escaped = normalized.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    records = session.scalars(_article_query()).all()

    if not normalized:
        return [hydrate_article(record) for record in records]

    filtered_records = session.scalars(
        _article_query().join(ArticleSectionRecord, ArticleSectionRecord.article_id == ArticleRecord.id).where(
            or_(
                ArticleRecord.title.ilike(f"%{escaped}%", escape="\\"),
                ArticleRecord.summary.ilike(f"%{escaped}%", escape="\\"),
                ArticleSectionRecord.content.ilike(f"%{escaped}%", escape="\\"),
            )
        )
    ).unique().all()

    candidate_records = filtered_records or records

    scored_matches: list[tuple[int, Article]] = []
    for record in candidate_records:
        article = hydrate_article(record)
        title = article.title.lower()
        summary = article.summary.lower()
        sections = " ".join(section.content for section in article.sections).lower()
        related_topics = " ".join(article.related_topics).lower()
        score = 0

        if normalized in title:
            score += 10
        if normalized in summary:
            score += 6
        if normalized in related_topics:
            score += 4
        if normalized in sections:
            score += 3

        for term in normalized.split():
            if term in title:
                score += 3
            if term in summary:
                score += 2
            if term in related_topics:
                score += 2
            if term in sections:
                score += 1

        if score > 0:
            scored_matches.append((score, article))

    if not scored_matches:
        return [hydrate_article(record) for record in records]

    scored_matches.sort(key=lambda item: item[0], reverse=True)
    return [article for _, article in scored_matches]


def create_article_suggestion(
    session: Session, article_slug: str, payload: ArticleSuggestionCreate, user: AuthUser
) -> ArticleSuggestion | None:
    article = session.scalars(select(ArticleRecord).where(ArticleRecord.slug == article_slug)).first()
    if article is None:
        return None

    record = ArticleSuggestionRecord(
        article_id=article.id,
        contributor_name=user.display_name,
        contributor_email=user.email,
        suggestion_type=payload.suggestion_type,
        summary=payload.summary,
        proposed_text=payload.proposed_text,
        source_url=payload.source_url,
        status="pending",
    )
    session.add(record)
    session.flush()
    session.add(
        ReviewQueueItemRecord(
            article_id=article.id,
            subject_type="suggestion",
            subject_id=record.id,
            priority="normal",
            status="pending",
        )
    )
    session.add(
        AuditLogRecord(
            actor_email=user.email,
            actor_role=user.role,
            action="article.suggestion.created",
            subject_type="article_suggestion",
            subject_id=record.id,
            details_json=json.dumps({"article_slug": article.slug}),
        )
    )
    session.commit()
    session.refresh(record)

    return ArticleSuggestion(
        id=record.id,
        article_slug=article.slug,
        contributor_name=record.contributor_name,
        contributor_email=record.contributor_email,
        suggestion_type=record.suggestion_type,
        summary=record.summary,
        proposed_text=record.proposed_text,
        source_url=record.source_url,
        status=record.status,
        created_at=record.created_at.isoformat(),
    )


def list_article_suggestions(session: Session, article_slug: str) -> list[ArticleSuggestion] | None:
    article = session.scalars(select(ArticleRecord).where(ArticleRecord.slug == article_slug)).first()
    if article is None:
        return None

    records = session.scalars(
        select(ArticleSuggestionRecord)
        .where(
            ArticleSuggestionRecord.article_id == article.id,
            ArticleSuggestionRecord.status == "approved",
        )
        .order_by(ArticleSuggestionRecord.created_at.desc())
    ).all()

    return [
        ArticleSuggestion(
            id=record.id,
            article_slug=article.slug,
            contributor_name=record.contributor_name,
            contributor_email=record.contributor_email,
            suggestion_type=record.suggestion_type,
            summary=record.summary,
            proposed_text=record.proposed_text,
            source_url=record.source_url,
            status=record.status,
            created_at=record.created_at.isoformat(),
        )
        for record in records
    ]


def create_source_submission(
    session: Session, article_slug: str, payload: SourceSubmissionCreate, user: AuthUser
) -> SourceSubmission | None:
    article = session.scalars(select(ArticleRecord).where(ArticleRecord.slug == article_slug)).first()
    if article is None:
        return None

    record = ArticleSourceSubmissionRecord(
        article_id=article.id,
        contributor_name=user.display_name,
        contributor_email=user.email,
        title=payload.title,
        publisher=payload.publisher,
        url=payload.url,
        rationale=payload.rationale,
        status="pending",
    )
    session.add(record)
    session.flush()
    session.add(
        ReviewQueueItemRecord(
            article_id=article.id,
            subject_type="source_submission",
            subject_id=record.id,
            priority="normal",
            status="pending",
        )
    )
    session.add(
        AuditLogRecord(
            actor_email=user.email,
            actor_role=user.role,
            action="article.source_submission.created",
            subject_type="article_source_submission",
            subject_id=record.id,
            details_json=json.dumps({"article_slug": article.slug}),
        )
    )
    session.commit()
    session.refresh(record)

    return SourceSubmission(
        id=record.id,
        article_slug=article.slug,
        contributor_name=record.contributor_name,
        contributor_email=record.contributor_email,
        title=record.title,
        publisher=record.publisher,
        url=record.url,
        rationale=record.rationale,
        status=record.status,
        created_at=record.created_at.isoformat(),
    )


def get_contributor_overview(session: Session, contributor_email: str) -> ContributorOverview:
    suggestions = [
        ArticleSuggestion(
            id=record.id,
            article_slug=record.article.slug,
            contributor_name=record.contributor_name,
            contributor_email=record.contributor_email,
            suggestion_type=record.suggestion_type,
            summary=record.summary,
            proposed_text=record.proposed_text,
            source_url=record.source_url,
            status=record.status,
            created_at=record.created_at.isoformat(),
        )
        for record in session.scalars(
            select(ArticleSuggestionRecord)
            .join(ArticleRecord, ArticleSuggestionRecord.article_id == ArticleRecord.id)
            .options(selectinload(ArticleSuggestionRecord.article))
            .where(ArticleSuggestionRecord.contributor_email == contributor_email)
            .order_by(ArticleSuggestionRecord.created_at.desc())
        ).all()
    ]

    source_submissions = [
        SourceSubmission(
            id=record.id,
            article_slug=record.article.slug,
            contributor_name=record.contributor_name,
            contributor_email=record.contributor_email,
            title=record.title,
            publisher=record.publisher,
            url=record.url,
            rationale=record.rationale,
            status=record.status,
            created_at=record.created_at.isoformat(),
        )
        for record in session.scalars(
            select(ArticleSourceSubmissionRecord)
            .join(ArticleRecord, ArticleSourceSubmissionRecord.article_id == ArticleRecord.id)
            .options(selectinload(ArticleSourceSubmissionRecord.article))
            .where(ArticleSourceSubmissionRecord.contributor_email == contributor_email)
            .order_by(ArticleSourceSubmissionRecord.created_at.desc())
        ).all()
    ]

    return ContributorOverview(
        contributor_email=contributor_email,
        suggestion_count=len(suggestions),
        source_submission_count=len(source_submissions),
        suggestions=suggestions,
        source_submissions=source_submissions,
    )


def get_user_by_email(session: Session, email: str) -> AuthUser | None:
    record = session.scalars(select(UserRecord).where(UserRecord.email == email, UserRecord.status == "active")).first()
    if record is None:
        return None
    return AuthUser(id=record.id, email=record.email, display_name=record.display_name, role=record.role)


def create_auth_session(session: Session, payload: AuthLoginRequest) -> AuthSession | None:
    if not _EMAIL_PATTERN.fullmatch(payload.email):
        return None
    record = session.scalars(select(UserRecord).where(UserRecord.email == payload.email, UserRecord.status == "active")).first()
    if record is None:
        return None

    now = datetime.now(UTC)
    session.execute(delete(SessionTokenRecord).where(SessionTokenRecord.expires_at <= now))
    existing_sessions = session.scalars(
        select(SessionTokenRecord)
        .where(SessionTokenRecord.user_id == record.id)
        .order_by(SessionTokenRecord.created_at.asc())
    ).all()
    sessions_to_remove = max(0, len(existing_sessions) - settings.max_sessions_per_user + 1)
    for stale_session in existing_sessions[:sessions_to_remove]:
        session.delete(stale_session)

    raw_token = f"wikiai_{secrets.token_urlsafe(32)}"
    expires_at = now + timedelta(hours=settings.session_ttl_hours)
    token_record = SessionTokenRecord(
        user_id=record.id,
        token_hash=_hash_token(raw_token),
        expires_at=expires_at,
    )
    session.add(token_record)
    session.flush()
    session.add(
        AuditLogRecord(
            actor_email=record.email,
            actor_role=record.role,
            action="auth.login",
            subject_type="auth_session",
            subject_id=token_record.id,
            details_json=json.dumps({"email": record.email}),
        )
    )
    session.commit()
    session.refresh(token_record)
    return AuthSession(
        token=raw_token,
        expires_at=expires_at.isoformat(),
        user=AuthUser(id=record.id, email=record.email, display_name=record.display_name, role=record.role),
    )


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_user_by_token(session: Session, token: str) -> AuthUser | None:
    record = session.scalars(
        select(UserRecord)
        .join(SessionTokenRecord, SessionTokenRecord.user_id == UserRecord.id)
        .where(
            SessionTokenRecord.token_hash == _hash_token(token),
            SessionTokenRecord.expires_at > datetime.now(UTC),
        )
    ).first()
    if record is None:
        return None
    return AuthUser(id=record.id, email=record.email, display_name=record.display_name, role=record.role)


def delete_auth_session(session: Session, token: str) -> bool:
    record = session.scalars(
        select(SessionTokenRecord).where(SessionTokenRecord.token_hash == _hash_token(token))
    ).first()
    if record is None:
        return False
    user = record.user
    session.add(
        AuditLogRecord(
            actor_email=user.email if user else None,
            actor_role=user.role if user else None,
            action="auth.logout",
            subject_type="auth_session",
            subject_id=record.id,
            details_json=None,
        )
    )
    session.delete(record)
    session.commit()
    return True


def _hydrate_queue_item(session: Session, record: ReviewQueueItemRecord) -> ReviewQueueItem:
    summary = ""
    contributor_name = ""
    contributor_email = None

    if record.subject_type == "suggestion":
        subject = session.get(ArticleSuggestionRecord, record.subject_id)
        if subject is not None:
            summary = subject.summary
            contributor_name = subject.contributor_name
            contributor_email = subject.contributor_email
    elif record.subject_type == "source_submission":
        subject = session.get(ArticleSourceSubmissionRecord, record.subject_id)
        if subject is not None:
            summary = subject.title
            contributor_name = subject.contributor_name
            contributor_email = subject.contributor_email

    return ReviewQueueItem(
        id=record.id,
        article_slug=record.article.slug,
        article_title=record.article.title,
        subject_type=record.subject_type,
        subject_id=record.subject_id,
        priority=record.priority,
        status=record.status,
        assigned_reviewer_email=record.assigned_reviewer_email,
        summary=summary,
        contributor_name=contributor_name,
        contributor_email=contributor_email,
        created_at=record.created_at.isoformat(),
        decisions=[
            ReviewDecision(
                id=decision.id,
                queue_item_id=decision.queue_item_id,
                reviewer_email=decision.reviewer_email,
                decision=decision.decision,
                notes=decision.notes,
                created_at=decision.created_at.isoformat(),
            )
            for decision in sorted(record.decisions, key=lambda item: item.created_at, reverse=True)
        ],
    )


def list_review_queue(
    session: Session, status: str | None = None, subject_type: str | None = None
) -> list[ReviewQueueItem]:
    query = (
        select(ReviewQueueItemRecord)
        .join(ArticleRecord, ReviewQueueItemRecord.article_id == ArticleRecord.id)
        .options(
            selectinload(ReviewQueueItemRecord.article),
            selectinload(ReviewQueueItemRecord.decisions),
        )
        .order_by(ReviewQueueItemRecord.created_at.asc())
    )
    if status:
        query = query.where(ReviewQueueItemRecord.status == status)
    if subject_type:
        query = query.where(ReviewQueueItemRecord.subject_type == subject_type)

    records = session.scalars(query).all()
    return [_hydrate_queue_item(session, record) for record in records]


def review_queue_overview(
    session: Session, status: str | None = None, subject_type: str | None = None
) -> ReviewerOverview:
    all_items = list_review_queue(session)
    filtered_items = [
        item
        for item in all_items
        if (status is None or item.status == status)
        and (subject_type is None or item.subject_type == subject_type)
    ]
    return ReviewerOverview(
        pending_count=sum(1 for item in all_items if item.status == "pending"),
        approved_count=sum(1 for item in all_items if item.status == "approved"),
        rejected_count=sum(1 for item in all_items if item.status == "rejected"),
        items=filtered_items,
    )


def create_review_decision(
    session: Session, queue_item_id: str, payload: ReviewDecisionCreate, user: AuthUser
) -> ReviewDecision | None:
    queue_item = session.get(ReviewQueueItemRecord, queue_item_id)
    if queue_item is None:
        return None

    contributor_email = _review_subject_contributor_email(session, queue_item)
    if contributor_email == user.email:
        raise PermissionError("Reviewers cannot decide on their own submissions")
    if queue_item.assigned_reviewer_email not in (None, user.email):
        raise ValueError("Queue item is assigned to another reviewer")

    result = session.execute(
        update(ReviewQueueItemRecord)
        .where(
            ReviewQueueItemRecord.id == queue_item_id,
            ReviewQueueItemRecord.status == "pending",
            or_(
                ReviewQueueItemRecord.assigned_reviewer_email.is_(None),
                ReviewQueueItemRecord.assigned_reviewer_email == user.email,
            ),
        )
        .values(status=payload.decision, assigned_reviewer_email=user.email)
    )
    if result.rowcount != 1:
        session.rollback()
        raise ValueError("Queue item is assigned to another reviewer or has already been decided")

    session.refresh(queue_item)
    queue_item.assigned_reviewer_email = user.email

    if queue_item.subject_type == "suggestion":
        subject = session.get(ArticleSuggestionRecord, queue_item.subject_id)
        if subject is not None:
            subject.status = payload.decision
    elif queue_item.subject_type == "source_submission":
        subject = session.get(ArticleSourceSubmissionRecord, queue_item.subject_id)
        if subject is not None:
            subject.status = payload.decision

    decision = ReviewDecisionRecord(
        queue_item_id=queue_item.id,
        reviewer_email=user.email,
        decision=payload.decision,
        notes=payload.notes,
    )
    session.add(decision)
    session.add(
        AuditLogRecord(
            actor_email=user.email,
            actor_role=user.role,
            action="review.decision.created",
            subject_type="review_queue_item",
            subject_id=queue_item.id,
            details_json=json.dumps({"decision": payload.decision}),
        )
    )
    session.commit()
    session.refresh(decision)

    return ReviewDecision(
        id=decision.id,
        queue_item_id=decision.queue_item_id,
        reviewer_email=decision.reviewer_email,
        decision=decision.decision,
        notes=decision.notes,
        created_at=decision.created_at.isoformat(),
    )


def assign_review_queue_item(
    session: Session, queue_item_id: str, user: AuthUser
) -> ReviewAssignment | None:
    queue_item = session.get(ReviewQueueItemRecord, queue_item_id)
    if queue_item is None:
        return None

    result = session.execute(
        update(ReviewQueueItemRecord)
        .where(
            ReviewQueueItemRecord.id == queue_item_id,
            ReviewQueueItemRecord.status == "pending",
            or_(
                ReviewQueueItemRecord.assigned_reviewer_email.is_(None),
                ReviewQueueItemRecord.assigned_reviewer_email == user.email,
            ),
        )
        .values(assigned_reviewer_email=user.email)
    )
    if result.rowcount != 1:
        session.rollback()
        raise ValueError("Queue item is already assigned or decided")
    session.refresh(queue_item)
    session.add(
        AuditLogRecord(
            actor_email=user.email,
            actor_role=user.role,
            action="review.assignment.created",
            subject_type="review_queue_item",
            subject_id=queue_item.id,
            details_json=json.dumps({"assigned_reviewer_email": user.email}),
        )
    )
    session.commit()
    session.refresh(queue_item)

    return ReviewAssignment(
        queue_item_id=queue_item.id,
        assigned_reviewer_email=user.email,
        status=queue_item.status,
    )


def _review_subject_contributor_email(
    session: Session, queue_item: ReviewQueueItemRecord
) -> str | None:
    if queue_item.subject_type == "suggestion":
        subject = session.get(ArticleSuggestionRecord, queue_item.subject_id)
    elif queue_item.subject_type == "source_submission":
        subject = session.get(ArticleSourceSubmissionRecord, queue_item.subject_id)
    else:
        subject = None
    return subject.contributor_email if subject is not None else None


def list_audit_logs(session: Session, limit: int = 50, action: str | None = None) -> list[AuditLogEntry]:
    query = select(AuditLogRecord).order_by(AuditLogRecord.created_at.desc()).limit(limit)
    if action:
        query = query.where(AuditLogRecord.action == action)

    records = session.scalars(query).all()
    return [
        AuditLogEntry(
            id=record.id,
            actor_email=record.actor_email,
            actor_role=record.actor_role,
            action=record.action,
            subject_type=record.subject_type,
            subject_id=record.subject_id,
            details_json=record.details_json,
            created_at=record.created_at.isoformat(),
        )
        for record in records
    ]


def get_admin_overview(session: Session) -> AdminOverview:
    recent = list_audit_logs(session, limit=20)
    return AdminOverview(
        audit_event_count=session.query(AuditLogRecord).count(),
        review_queue_count=session.query(ReviewQueueItemRecord).count(),
        active_session_count=session.query(SessionTokenRecord)
        .filter(SessionTokenRecord.expires_at > datetime.now(UTC))
        .count(),
        recent_audit_entries=recent,
    )


def list_auth_sessions(session: Session, limit: int = 100) -> list[AuthSessionInfo]:
    records = session.scalars(
        select(SessionTokenRecord)
        .join(UserRecord, SessionTokenRecord.user_id == UserRecord.id)
        .options(selectinload(SessionTokenRecord.user))
        .where(SessionTokenRecord.expires_at > datetime.now(UTC))
        .order_by(SessionTokenRecord.created_at.desc())
        .limit(limit)
    ).all()
    return [
        AuthSessionInfo(
            id=record.id,
            user_email=record.user.email,
            user_role=record.user.role,
            expires_at=record.expires_at.isoformat(),
            created_at=record.created_at.isoformat(),
        )
        for record in records
    ]


def admin_revoke_session(session: Session, session_id: str, user: AuthUser) -> bool:
    record = session.get(SessionTokenRecord, session_id)
    if record is None:
        return False
    target_user = record.user
    session.add(
        AuditLogRecord(
            actor_email=user.email,
            actor_role=user.role,
            action="admin.session.revoked",
            subject_type="auth_session",
            subject_id=record.id,
            details_json=json.dumps(
                {"revoked_user_email": target_user.email if target_user else ""}
            ),
        )
    )
    session.delete(record)
    session.commit()
    return True


def _hydrate_claim(article_slug: str, record: ClaimRecord) -> Claim:
    metrics_record = None
    if record.confidence_metrics:
        metrics_record = max(record.confidence_metrics, key=lambda m: m.computed_at)
    return Claim(
        id=record.id,
        article_slug=article_slug,
        claim_text=record.claim_text,
        claim_type=record.claim_type,
        section_key=record.section_key,
        status=record.status,
        confidence=record.confidence,
        citations=[
            ClaimCitation(
                id=c.id,
                source_id=c.source_id,
                evidence_span=c.evidence_span,
                support_type=c.support_type,
            )
            for c in record.citations
        ],
        confidence_metrics=(
            ConfidenceMetrics(
                id=metrics_record.id,
                subject_type=metrics_record.subject_type,
                subject_id=metrics_record.subject_id,
                overall_score=metrics_record.overall_score,
                source_quality_score=metrics_record.source_quality_score,
                cross_source_agreement_score=metrics_record.cross_source_agreement_score,
                freshness_score=metrics_record.freshness_score,
                coverage_score=metrics_record.coverage_score,
                human_review_score=metrics_record.human_review_score,
                computed_at=metrics_record.computed_at.isoformat(),
            )
            if metrics_record
            else None
        ),
        contradictions=[
            Contradiction(
                id=c.id,
                claim_id=c.claim_id,
                source_id=c.source_id,
                contradiction_type=c.contradiction_type,
                severity=c.severity,
                details_json=c.details_json,
                status=c.status,
            )
            for c in record.contradictions
        ],
    )


def get_claims_by_article(session: Session, article_slug: str) -> list[Claim] | None:
    article = session.scalars(select(ArticleRecord).where(ArticleRecord.slug == article_slug)).first()
    if article is None:
        return None
    records = session.scalars(
        select(ClaimRecord)
        .options(
            selectinload(ClaimRecord.citations),
            selectinload(ClaimRecord.contradictions),
            selectinload(ClaimRecord.confidence_metrics),
        )
        .where(ClaimRecord.article_id == article.id)
        .order_by(ClaimRecord.created_at.asc())
    ).all()
    return [_hydrate_claim(article.slug, r) for r in records]


def get_claim_by_id(session: Session, claim_id: str) -> Claim | None:
    record = session.scalars(
        select(ClaimRecord)
        .options(
            selectinload(ClaimRecord.citations),
            selectinload(ClaimRecord.contradictions),
            selectinload(ClaimRecord.confidence_metrics),
        )
        .where(ClaimRecord.id == claim_id)
    ).first()
    if record is None:
        return None
    article = session.get(ArticleRecord, record.article_id)
    return _hydrate_claim(article.slug if article else "", record)


def list_entities(session: Session) -> list[Entity]:
    records = session.scalars(select(EntityRecord).order_by(EntityRecord.name.asc())).all()
    return [
        Entity(
            id=r.id,
            name=r.name,
            entity_type=r.entity_type,
            canonical_slug=r.canonical_slug,
            description=r.description,
        )
        for r in records
    ]


def get_entity_graph(session: Session, slug: str) -> EntityGraph | None:
    record = session.scalars(
        select(EntityRecord)
        .options(
            selectinload(EntityRecord.outgoing_relationships).selectinload(
                EntityRelationshipRecord.object_entity
            ),
            selectinload(EntityRecord.incoming_relationships).selectinload(
                EntityRelationshipRecord.subject_entity
            ),
            selectinload(EntityRecord.article_entities).selectinload(ArticleEntityRecord.article),
        )
        .where(EntityRecord.canonical_slug == slug)
    ).first()
    if record is None:
        return None
    outgoing = [
        EntityRelationship(
            id=rel.id,
            subject_slug=record.canonical_slug,
            subject_name=record.name,
            predicate=rel.predicate,
            object_slug=rel.object_entity.canonical_slug,
            object_name=rel.object_entity.name,
            confidence=rel.confidence,
        )
        for rel in record.outgoing_relationships
    ]
    incoming = [
        EntityRelationship(
            id=rel.id,
            subject_slug=rel.subject_entity.canonical_slug,
            subject_name=rel.subject_entity.name,
            predicate=rel.predicate,
            object_slug=record.canonical_slug,
            object_name=record.name,
            confidence=rel.confidence,
        )
        for rel in record.incoming_relationships
    ]
    return EntityGraph(
        entity=Entity(
            id=record.id,
            name=record.name,
            entity_type=record.entity_type,
            canonical_slug=record.canonical_slug,
            description=record.description,
        ),
        relationships=outgoing + incoming,
        article_slugs=[ae.article.slug for ae in record.article_entities],
    )
