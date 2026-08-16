import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.database import SessionLocal
from app.main import (
    admin_audit_logs,
    admin_overview,
    admin_revoke_auth_session,
    admin_sessions,
    assign_review_item,
    auth_login,
    auth_session,
    article_detail,
    article_suggestions,
    articles,
    contributor_overview,
    health,
    review_queue,
    reviewer_overview,
    search,
    submit_review_decision,
    submit_article_source,
    submit_article_suggestion,
)
from app.models import ArticleSuggestionCreate, AuthLoginRequest, ChatRequest, ReviewDecisionCreate, SourceSubmissionCreate
from app.services import build_search_response


def login_user(session, email: str):
    return auth_login(AuthLoginRequest(email=email), session)


def test_health() -> None:
    payload = health()
    assert payload["status"] == "ok"


def test_article_detail() -> None:
    session = SessionLocal()
    payload = article_detail("quantum-computing", session)
    assert payload.slug == "quantum-computing"
    assert payload.sources
    session.close()


def test_articles_summary_list() -> None:
    session = SessionLocal()
    payload = articles(session)
    assert payload
    assert payload[0].slug
    session.close()


def test_search_returns_grounded_payload() -> None:
    session = SessionLocal()
    payload = search("quantum", session)
    assert payload.answer
    assert payload.sources
    assert payload.articles
    session.close()


def test_service_search_response() -> None:
    session = SessionLocal()
    payload = build_search_response(session, "inflation in brazil")
    assert "inflation" in payload.answer.lower()
    assert payload.articles[0].slug == "inflation-in-brazil"
    session.close()


def test_submit_article_suggestion() -> None:
    session = SessionLocal()
    auth = login_user(session, "contributor@example.com")
    payload = submit_article_suggestion(
        "quantum-computing",
        ArticleSuggestionCreate(
            suggestion_type="correction",
            summary="Clarify the practical limits section.",
            proposed_text="Add a sentence about error-correction overhead.",
            source_url="https://example.com/source",
        ),
        session,
        auth.user,
    )
    assert payload.status == "pending"
    assert payload.article_slug == "quantum-computing"
    session.close()


def test_list_article_suggestions() -> None:
    session = SessionLocal()
    auth = login_user(session, "contributor@example.com")
    suggestion = submit_article_suggestion(
        "quantum-computing",
        ArticleSuggestionCreate(
            summary="Tighten wording in the overview section.",
        ),
        session,
        auth.user,
    )
    reviewer = login_user(session, "reviewer@example.com")
    queue_item = next(
        item
        for item in review_queue("pending", None, session, reviewer.user)
        if item.subject_id == suggestion.id
    )
    submit_review_decision(
        queue_item.id,
        ReviewDecisionCreate(decision="approved"),
        session,
        reviewer.user,
    )
    payload = article_suggestions("quantum-computing", session)
    assert payload
    assert payload[0].article_slug == "quantum-computing"
    assert not hasattr(payload[0], "contributor_email")
    session.close()


def test_submit_article_source() -> None:
    session = SessionLocal()
    auth = login_user(session, "contributor@example.com")
    payload = submit_article_source(
        "inflation-in-brazil",
        SourceSubmissionCreate(
            title="Brazil Inflation Outlook",
            publisher="OECD",
            url="https://example.com/oecd-brazil-inflation",
            rationale="Adds a complementary macroeconomic source for current inflation drivers.",
        ),
        session,
        auth.user,
    )
    assert payload.publisher == "OECD"
    assert payload.status == "pending"
    session.close()


def test_contributor_overview() -> None:
    session = SessionLocal()
    auth = login_user(session, "contributor@example.com")
    submit_article_suggestion(
        "quantum-computing",
        ArticleSuggestionCreate(
            summary="Add hardware examples.",
        ),
        session,
        auth.user,
    )
    submit_article_source(
        "quantum-computing",
        SourceSubmissionCreate(
            title="Hardware Landscape",
            publisher="MIT",
            url="https://example.com/hardware",
            rationale="Supports a broader view of current hardware architectures.",
        ),
        session,
        auth.user,
    )
    payload = contributor_overview(session, auth.user)
    assert payload.suggestion_count == 1
    assert payload.source_submission_count == 1
    session.close()


def test_review_queue_lists_pending_items() -> None:
    session = SessionLocal()
    auth = login_user(session, "contributor@example.com")
    submit_article_suggestion(
        "quantum-computing",
        ArticleSuggestionCreate(
            summary="Add benchmark caveat.",
        ),
        session,
        auth.user,
    )
    reviewer = login_user(session, "reviewer@example.com")
    payload = review_queue("pending", None, session, reviewer.user)
    assert payload
    assert payload[0].status == "pending"
    session.close()


def test_submit_review_decision_updates_queue_and_subject() -> None:
    session = SessionLocal()
    contributor = login_user(session, "contributor@example.com")
    submit_article_source(
        "inflation-in-brazil",
        SourceSubmissionCreate(
            title="Regional Inflation Data",
            publisher="IBGE",
            url="https://example.com/ibge",
            rationale="Adds regional breakdown.",
        ),
        session,
        contributor.user,
    )
    reviewer = login_user(session, "reviewer@example.com")
    queue_items = review_queue("pending", None, session, reviewer.user)
    source_item = next(item for item in queue_items if item.subject_type == "source_submission")
    decision = submit_review_decision(
        source_item.id,
        ReviewDecisionCreate(
            decision="approved",
            notes="Source is relevant and credible for the current section.",
        ),
        session,
        reviewer.user,
    )
    assert decision.decision == "approved"
    overview = reviewer_overview(None, None, session, reviewer.user)
    assert overview.approved_count >= 1
    session.close()


def test_review_decision_is_final() -> None:
    session = SessionLocal()
    contributor = login_user(session, "contributor@example.com")
    submit_article_suggestion(
        "quantum-computing",
        ArticleSuggestionCreate(summary="Add a finality test."),
        session,
        contributor.user,
    )
    reviewer = login_user(session, "reviewer@example.com")
    item = review_queue("pending", None, session, reviewer.user)[0]
    submit_review_decision(
        item.id,
        ReviewDecisionCreate(decision="approved"),
        session,
        reviewer.user,
    )

    with pytest.raises(HTTPException) as exc:
        submit_review_decision(
            item.id,
            ReviewDecisionCreate(decision="rejected"),
            session,
            reviewer.user,
        )

    assert exc.value.status_code == 409
    assert "already been decided" in exc.value.detail
    session.close()


@pytest.mark.parametrize("summary", ["", "   "])
def test_suggestion_summary_rejects_blank_values(summary: str) -> None:
    with pytest.raises(ValidationError):
        ArticleSuggestionCreate(summary=summary)


def test_submission_fields_have_maximum_lengths() -> None:
    with pytest.raises(ValidationError):
        ArticleSuggestionCreate(summary="x" * 501)
    with pytest.raises(ValidationError):
        SourceSubmissionCreate(title="x" * 256, publisher="Publisher", url="https://example.com", rationale="Useful")
    with pytest.raises(ValidationError):
        ChatRequest(question="x" * 2_001)


@pytest.mark.parametrize("email", ["not-an-email", "missing@domain", "@example.com", ""])
def test_login_rejects_malformed_email_without_querying(email: str) -> None:
    session = SessionLocal()
    with pytest.raises(HTTPException) as exc:
        auth_login(AuthLoginRequest(email=email), session)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"
    session.close()


def test_auth_session_returns_user() -> None:
    session = SessionLocal()
    auth = login_user(session, "reviewer@example.com")
    payload = auth_session(auth.user)
    assert payload.role == "reviewer"
    session.close()


def test_assign_review_item() -> None:
    session = SessionLocal()
    contributor = login_user(session, "contributor@example.com")
    submit_article_suggestion(
        "quantum-computing",
        ArticleSuggestionCreate(summary="Add implementation examples."),
        session,
        contributor.user,
    )
    reviewer = login_user(session, "reviewer@example.com")
    queue_items = review_queue("pending", None, session, reviewer.user)
    assignment = assign_review_item(queue_items[0].id, session, reviewer.user)
    assert assignment.assigned_reviewer_email == "reviewer@example.com"
    session.close()


def test_admin_overview_and_audit_logs() -> None:
    session = SessionLocal()
    contributor = login_user(session, "contributor@example.com")
    submit_article_suggestion(
        "quantum-computing",
        ArticleSuggestionCreate(summary="Add a practical example."),
        session,
        contributor.user,
    )
    admin = login_user(session, "admin@example.com")
    overview = admin_overview(session, admin.user)
    assert overview.audit_event_count >= 1
    audit_logs = admin_audit_logs(20, None, session, admin.user)
    assert any(entry.action == "article.suggestion.created" for entry in audit_logs)
    session.close()


def test_admin_can_list_and_revoke_sessions() -> None:
    session = SessionLocal()
    contributor = login_user(session, "contributor@example.com")
    admin = login_user(session, "admin@example.com")
    sessions = admin_sessions(100, session, admin.user)
    contributor_session = next(item for item in sessions if item.user_email == "contributor@example.com")
    result = admin_revoke_auth_session(contributor_session.id, session, admin.user)
    assert result["ok"] is True
    remaining = admin_sessions(100, session, admin.user)
    assert all(item.id != contributor_session.id for item in remaining)
    session.close()
