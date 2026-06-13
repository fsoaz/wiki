from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .auth import get_current_user, require_admin, require_contributor, require_reviewer
from .config import settings
from .database import Base, SessionLocal, engine, get_session
from .models import (
    AdminOverview,
    Article,
    ArticleSuggestion,
    ArticleSuggestionCreate,
    ArticleSummary,
    AuditLogEntry,
    AuthLoginRequest,
    AuthSession,
    AuthSessionInfo,
    AuthUser,
    ChatRequest,
    ChatResponse,
    Claim,
    ContributorOverview,
    Entity,
    EntityGraph,
    ReviewAssignment,
    ReviewDecision,
    ReviewDecisionCreate,
    ReviewerOverview,
    ReviewQueueItem,
    SearchResponse,
    SourceSubmission,
    SourceSubmissionCreate,
)
from .repository import (
    get_admin_overview,
    assign_review_queue_item,
    create_article_suggestion,
    create_auth_session,
    create_review_decision,
    create_source_submission,
    delete_auth_session,
    get_article_by_slug,
    get_claim_by_id,
    get_claims_by_article,
    get_contributor_overview,
    get_entity_graph,
    get_user_by_token,
    list_audit_logs,
    list_auth_sessions,
    list_article_suggestions,
    list_articles,
    list_entities,
    list_review_queue,
    review_queue_overview,
    admin_revoke_session,
)
from .seed import seed_articles, seed_claims_and_entities, seed_users
from .services import build_chat_response, build_jsonld_article, build_jsonld_export, build_search_response, summarize_articles


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_users(session)
        seed_articles(session)
        seed_claims_and_entities(session)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "WikiAI epistemic database API. "
        "The database is the product — articles, atomic claims, source citations, confidence scores, "
        "knowledge graph entities, and JSON-LD export are all first-class API resources. "
        "The website is one view into this data."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin, "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}


@app.post("/api/v1/auth/login", response_model=AuthSession)
def auth_login(payload: AuthLoginRequest, session: Session = Depends(get_session)) -> AuthSession:
    auth_session = create_auth_session(session, payload)
    if auth_session is None:
        raise HTTPException(status_code=404, detail="User not found")
    return auth_session


@app.get("/api/v1/auth/session", response_model=AuthUser)
def auth_session(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    return user


@app.post("/api/v1/auth/logout")
def auth_logout(
    authorization: str | None = Query(default=None),
    session: Session = Depends(get_session),
) -> dict[str, bool]:
    token = authorization
    if token is None:
        return {"ok": False}
    return {"ok": delete_auth_session(session, token)}


@app.get("/api/v1/admin/overview", response_model=AdminOverview)
def admin_overview(
    session: Session = Depends(get_session),
    _: AuthUser = Depends(require_admin),
) -> AdminOverview:
    return get_admin_overview(session)


@app.get("/api/v1/admin/audit", response_model=list[AuditLogEntry])
def admin_audit_logs(
    limit: int = Query(default=50, ge=1, le=200),
    action: str | None = Query(default=None),
    session: Session = Depends(get_session),
    _: AuthUser = Depends(require_admin),
) -> list[AuditLogEntry]:
    return list_audit_logs(session, limit, action)


@app.get("/api/v1/admin/sessions", response_model=list[AuthSessionInfo])
def admin_sessions(
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
    _: AuthUser = Depends(require_admin),
) -> list[AuthSessionInfo]:
    return list_auth_sessions(session, limit)


@app.post("/api/v1/admin/sessions/{session_id}/revoke")
def admin_revoke_auth_session(
    session_id: str,
    session: Session = Depends(get_session),
    user: AuthUser = Depends(require_admin),
) -> dict[str, bool]:
    return {"ok": admin_revoke_session(session, session_id, user)}


@app.get("/api/v1/articles", response_model=list[ArticleSummary])
def articles(session: Session = Depends(get_session)) -> list[ArticleSummary]:
    return summarize_articles(list_articles(session))


@app.get("/api/v1/articles/{slug}", response_model=Article)
def article_detail(slug: str, session: Session = Depends(get_session)) -> Article:
    article = get_article_by_slug(session, slug)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@app.get("/api/v1/search", response_model=SearchResponse)
def search(
    q: str = Query("", min_length=0, max_length=200),
    session: Session = Depends(get_session),
) -> SearchResponse:
    return build_search_response(session, q)


@app.post("/api/v1/articles/{slug}/chat", response_model=ChatResponse)
def article_chat(slug: str, payload: ChatRequest, session: Session = Depends(get_session)) -> ChatResponse:
    article = get_article_by_slug(session, slug)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return build_chat_response(article, payload.question)


@app.post("/api/v1/articles/{slug}/suggestions", response_model=ArticleSuggestion, status_code=201)
def submit_article_suggestion(
    slug: str,
    payload: ArticleSuggestionCreate,
    session: Session = Depends(get_session),
    user: AuthUser = Depends(require_contributor),
) -> ArticleSuggestion:
    suggestion = create_article_suggestion(session, slug, payload, user)
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return suggestion


@app.get("/api/v1/articles/{slug}/suggestions", response_model=list[ArticleSuggestion])
def article_suggestions(slug: str, session: Session = Depends(get_session)) -> list[ArticleSuggestion]:
    suggestions = list_article_suggestions(session, slug)
    if suggestions is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return suggestions


@app.post("/api/v1/articles/{slug}/sources", response_model=SourceSubmission, status_code=201)
def submit_article_source(
    slug: str,
    payload: SourceSubmissionCreate,
    session: Session = Depends(get_session),
    user: AuthUser = Depends(require_contributor),
) -> SourceSubmission:
    submission = create_source_submission(session, slug, payload, user)
    if submission is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return submission


@app.get("/api/v1/contributors/overview", response_model=ContributorOverview)
def contributor_overview(
    session: Session = Depends(get_session),
    user: AuthUser = Depends(require_contributor),
) -> ContributorOverview:
    return get_contributor_overview(session, user.email)


@app.get("/api/v1/reviews/queue", response_model=list[ReviewQueueItem])
def review_queue(
    status: str | None = Query(default=None),
    subject_type: str | None = Query(default=None),
    session: Session = Depends(get_session),
    _: AuthUser = Depends(require_reviewer),
) -> list[ReviewQueueItem]:
    return list_review_queue(session, status, subject_type)


@app.get("/api/v1/reviews/overview", response_model=ReviewerOverview)
def reviewer_overview(
    status: str | None = Query(default=None),
    subject_type: str | None = Query(default=None),
    session: Session = Depends(get_session),
    _: AuthUser = Depends(require_reviewer),
) -> ReviewerOverview:
    return review_queue_overview(session, status, subject_type)


@app.post("/api/v1/reviews/queue/{queue_item_id}/assign", response_model=ReviewAssignment)
def assign_review_item(
    queue_item_id: str,
    session: Session = Depends(get_session),
    user: AuthUser = Depends(require_reviewer),
) -> ReviewAssignment:
    assignment = assign_review_queue_item(session, queue_item_id, user)
    if assignment is None:
        raise HTTPException(status_code=404, detail="Queue item not found")
    return assignment


@app.post("/api/v1/reviews/queue/{queue_item_id}/decision", response_model=ReviewDecision)
def submit_review_decision(
    queue_item_id: str,
    payload: ReviewDecisionCreate,
    session: Session = Depends(get_session),
    user: AuthUser = Depends(require_reviewer),
) -> ReviewDecision:
    decision = create_review_decision(session, queue_item_id, payload, user)
    if decision is None:
        raise HTTPException(status_code=404, detail="Queue item not found")
    return decision


# --- Epistemic database endpoints ---


@app.get("/api/v1/articles/{slug}/claims", response_model=list[Claim])
def article_claims(slug: str, session: Session = Depends(get_session)) -> list[Claim]:
    claims = get_claims_by_article(session, slug)
    if claims is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return claims


@app.get("/api/v1/claims/{claim_id}", response_model=Claim)
def claim_detail(claim_id: str, session: Session = Depends(get_session)) -> Claim:
    claim = get_claim_by_id(session, claim_id)
    if claim is None:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@app.get("/api/v1/entities", response_model=list[Entity])
def get_entities(session: Session = Depends(get_session)) -> list[Entity]:
    return list_entities(session)


@app.get("/api/v1/entities/{slug}", response_model=EntityGraph)
def entity_graph(slug: str, session: Session = Depends(get_session)) -> EntityGraph:
    graph = get_entity_graph(session, slug)
    if graph is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return graph


@app.get("/api/v1/articles/{slug}/jsonld")
def article_jsonld(slug: str, session: Session = Depends(get_session)) -> dict:
    article = get_article_by_slug(session, slug)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return build_jsonld_article(article)


@app.get("/api/v1/export")
def export_knowledge(
    format: str = Query(default="jsonld", pattern="^(jsonld)$"),
    session: Session = Depends(get_session),
) -> dict:
    all_articles = list_articles(session)
    all_entities = list_entities(session)
    return build_jsonld_export(all_articles, all_entities)
