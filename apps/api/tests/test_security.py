from datetime import UTC, datetime, timedelta
import hashlib
import json

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, select, text

from app.config import Settings
from app.database import Base, SessionLocal
from app.db_models import AuditLogRecord, SessionTokenRecord
from app.main import (
    article_suggestions,
    assign_review_item,
    auth_login,
    auth_logout,
    review_queue,
    submit_article_suggestion,
    submit_review_decision,
)
from app.models import ArticleSuggestionCreate, AuthLoginRequest, ReviewDecisionCreate
from app.rate_limit import FixedWindowRateLimiter
from app.repository import get_user_by_token
from app.schema import upgrade_legacy_auth_sessions


def login(session, email: str):
    return auth_login(AuthLoginRequest(email=email), session)


def test_session_stores_only_hash_and_expiry() -> None:
    session = SessionLocal()
    auth = login(session, "contributor@example.com")
    stored = session.scalars(select(SessionTokenRecord)).one()
    assert stored.token_hash == hashlib.sha256(auth.token.encode()).hexdigest()
    assert auth.token not in stored.token_hash
    assert stored.expires_at is not None
    assert get_user_by_token(session, auth.token).email == "contributor@example.com"
    session.close()


def test_expired_session_is_invalid_and_omitted() -> None:
    session = SessionLocal()
    auth = login(session, "contributor@example.com")
    stored = session.scalars(select(SessionTokenRecord)).one()
    stored.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    session.commit()
    assert get_user_by_token(session, auth.token) is None
    session.close()


def test_login_keeps_at_most_five_sessions_per_user() -> None:
    session = SessionLocal()
    for _ in range(7):
        login(session, "contributor@example.com")
    records = session.scalars(select(SessionTokenRecord)).all()
    assert len(records) == 5
    session.close()


def test_authenticated_logout_revokes_session() -> None:
    session = SessionLocal()
    auth = login(session, "contributor@example.com")
    response = auth_logout(auth.token, auth.user, session)
    assert response.status_code == 204
    assert get_user_by_token(session, auth.token) is None
    session.close()


def test_reviewer_cannot_decide_own_submission() -> None:
    session = SessionLocal()
    reviewer = login(session, "reviewer@example.com")
    suggestion = submit_article_suggestion(
        "quantum-computing",
        ArticleSuggestionCreate(summary="A reviewer-authored proposal."),
        session,
        reviewer.user,
    )
    item = next(
        item
        for item in review_queue("pending", None, session, reviewer.user)
        if item.subject_id == suggestion.id
    )
    with pytest.raises(HTTPException) as exc:
        submit_review_decision(
            item.id,
            ReviewDecisionCreate(decision="approved"),
            session,
            reviewer.user,
        )
    assert exc.value.status_code == 403
    session.close()


def test_reviewer_cannot_take_another_reviewers_assignment() -> None:
    session = SessionLocal()
    contributor = login(session, "contributor@example.com")
    suggestion = submit_article_suggestion(
        "quantum-computing",
        ArticleSuggestionCreate(summary="Assignment ownership test."),
        session,
        contributor.user,
    )
    reviewer = login(session, "reviewer@example.com")
    admin = login(session, "admin@example.com")
    item = next(
        item
        for item in review_queue("pending", None, session, reviewer.user)
        if item.subject_id == suggestion.id
    )
    assign_review_item(item.id, session, reviewer.user)
    with pytest.raises(HTTPException) as exc:
        assign_review_item(item.id, session, admin.user)
    assert exc.value.status_code == 409
    session.close()


def test_public_suggestions_exclude_pending_content() -> None:
    session = SessionLocal()
    contributor = login(session, "contributor@example.com")
    submit_article_suggestion(
        "quantum-computing",
        ArticleSuggestionCreate(summary="Not reviewed yet."),
        session,
        contributor.user,
    )
    assert article_suggestions("quantum-computing", session) == []
    session.close()


def test_audit_details_are_valid_json() -> None:
    session = SessionLocal()
    login(session, "contributor@example.com")
    records = session.scalars(select(AuditLogRecord)).all()
    assert all(json.loads(record.details_json) for record in records if record.details_json)
    session.close()


def test_fixed_window_rate_limiter_returns_retry_after() -> None:
    limiter = FixedWindowRateLimiter()
    limiter.check("test", limit=2, window_seconds=60)
    limiter.check("test", limit=2, window_seconds=60)
    with pytest.raises(HTTPException) as exc:
        limiter.check("test", limit=2, window_seconds=60)
    assert exc.value.status_code == 429
    assert int(exc.value.headers["Retry-After"]) >= 1


def test_cors_rejects_wildcard_and_production_localhost() -> None:
    with pytest.raises(ValueError):
        Settings(cors_origin="*")
    production = Settings(app_env="production", cors_origin="http://localhost:3000,https://wiki.example")
    assert production.cors_origins == ["https://wiki.example"]


def test_legacy_session_upgrade_invalidates_only_sessions(tmp_path) -> None:
    engine = create_engine(f"sqlite:///{tmp_path / 'legacy.db'}")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE marker (value TEXT NOT NULL)"))
        connection.execute(text("INSERT INTO marker VALUES ('preserved')"))
        connection.execute(
            text(
                "CREATE TABLE auth_sessions ("
                "id TEXT PRIMARY KEY, user_id TEXT NOT NULL, token TEXT NOT NULL, created_at TEXT NOT NULL)"
            )
        )
        connection.execute(
            text("INSERT INTO auth_sessions VALUES ('1', 'user', 'wikiai_secret', '2026-01-01')")
        )

    assert upgrade_legacy_auth_sessions(engine) is True
    Base.metadata.create_all(engine)
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT value FROM marker")) == "preserved"
        columns = {row[1] for row in connection.execute(text("PRAGMA table_info(auth_sessions)"))}
        assert "token_hash" in columns
        assert "token" not in columns
        assert connection.scalar(text("SELECT COUNT(*) FROM auth_sessions")) == 0
