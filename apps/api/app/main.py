from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .auth import get_bearer_token, get_current_user, require_admin, require_contributor, require_reviewer
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
    PublicArticleSuggestion,
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
from .rate_limit import rate_limiter
from .seed import seed_articles, seed_claims_and_entities, seed_users
from .schema import upgrade_legacy_auth_sessions
from .services import build_chat_response, build_jsonld_article, build_jsonld_export, build_search_response, summarize_articles


@asynccontextmanager
async def lifespan(_: FastAPI):
    upgrade_legacy_auth_sessions(engine)
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
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["Link", "Retry-After", "X-Total-Count"],
)


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def limit_login(request: Request) -> None:
    rate_limiter.check(f"login:{_client_ip(request)}", limit=5, window_seconds=60)


def limit_export(request: Request) -> None:
    rate_limiter.check(f"export:{_client_ip(request)}", limit=10, window_seconds=60)


def limit_contributions(user: AuthUser = Depends(require_contributor)) -> None:
    rate_limiter.check(f"contribution:{user.email}", limit=20, window_seconds=3_600)


@app.get("/health")
def health() -> dict[str, str]:
    """Return process liveness and the configured `WIKIAI_APP_ENV` value."""
    return {"status": "ok", "environment": settings.app_env}


@app.post("/api/v1/auth/login", response_model=AuthSession, dependencies=[Depends(limit_login)])
def auth_login(payload: AuthLoginRequest, session: Session = Depends(get_session)) -> AuthSession:
    """Create a time-limited demo session from a seeded email."""
    auth_session = create_auth_session(session, payload)
    if auth_session is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return auth_session


@app.get("/api/v1/auth/session", response_model=AuthUser)
def auth_session(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    """Return the user bound to the Bearer token."""
    return user


@app.post("/api/v1/auth/logout", status_code=204)
def auth_logout(
    token: str = Depends(get_bearer_token),
    _: AuthUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Response:
    """Delete the authenticated bearer session."""
    delete_auth_session(session, token)
    return Response(status_code=204)


@app.get("/api/v1/admin/overview", response_model=AdminOverview)
def admin_overview(
    session: Session = Depends(get_session),
    _: AuthUser = Depends(require_admin),
) -> AdminOverview:
    """Return queue counts, active session count, and recent audit entries. Admin role required."""
    return get_admin_overview(session)


@app.get("/api/v1/admin/audit", response_model=list[AuditLogEntry])
def admin_audit_logs(
    limit: int = Query(default=50, ge=1, le=200),
    action: str | None = Query(default=None),
    session: Session = Depends(get_session),
    _: AuthUser = Depends(require_admin),
) -> list[AuditLogEntry]:
    """List recent audit events. Admin role required. Filter with optional `action`."""
    return list_audit_logs(session, limit, action)


@app.get("/api/v1/admin/sessions", response_model=list[AuthSessionInfo])
def admin_sessions(
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_session),
    _: AuthUser = Depends(require_admin),
) -> list[AuthSessionInfo]:
    """List active demo sessions. Admin role required."""
    return list_auth_sessions(session, limit)


@app.post("/api/v1/admin/sessions/{session_id}/revoke")
def admin_revoke_auth_session(
    session_id: str,
    session: Session = Depends(get_session),
    user: AuthUser = Depends(require_admin),
) -> dict[str, bool]:
    """Revoke one demo session by id. Admin role required."""
    return {"ok": admin_revoke_session(session, session_id, user)}


@app.get("/api/v1/articles", response_model=list[ArticleSummary])
def articles(session: Session = Depends(get_session)) -> list[ArticleSummary]:
    """List published article summaries with confidence and last-verified dates."""
    return summarize_articles(list_articles(session))


@app.get("/api/v1/articles/{slug}", response_model=Article)
def article_detail(slug: str, session: Session = Depends(get_session)) -> Article:
    """Return one article by slug, including sections, sources, timeline, and trust metadata."""
    article = get_article_by_slug(session, slug)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@app.get("/api/v1/search", response_model=SearchResponse)
def search(
    q: str = Query("", min_length=0, max_length=200),
    session: Session = Depends(get_session),
) -> SearchResponse:
    """Search seeded article text. Returns a grounded answer plus matching articles and sources."""
    return build_search_response(session, q)


@app.post("/api/v1/articles/{slug}/chat", response_model=ChatResponse)
def article_chat(slug: str, payload: ChatRequest, session: Session = Depends(get_session)) -> ChatResponse:
    """Answer a question using only the named article's seeded content."""
    article = get_article_by_slug(session, slug)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return build_chat_response(article, payload.question)


@app.post(
    "/api/v1/articles/{slug}/suggestions",
    response_model=ArticleSuggestion,
    status_code=201,
    dependencies=[Depends(limit_contributions)],
)
def submit_article_suggestion(
    slug: str,
    payload: ArticleSuggestionCreate,
    session: Session = Depends(get_session),
    user: AuthUser = Depends(require_contributor),
) -> ArticleSuggestion:
    """Create an article improvement suggestion and a review-queue item. Contributor role required."""
    suggestion = create_article_suggestion(session, slug, payload, user)
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return suggestion


@app.get("/api/v1/articles/{slug}/suggestions", response_model=list[PublicArticleSuggestion])
def article_suggestions(slug: str, session: Session = Depends(get_session)) -> list[PublicArticleSuggestion]:
    """List suggestions submitted for an article without private contributor emails."""
    suggestions = list_article_suggestions(session, slug)
    if suggestions is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return [PublicArticleSuggestion.model_validate(item, from_attributes=True) for item in suggestions]


@app.post(
    "/api/v1/articles/{slug}/sources",
    response_model=SourceSubmission,
    status_code=201,
    dependencies=[Depends(limit_contributions)],
)
def submit_article_source(
    slug: str,
    payload: SourceSubmissionCreate,
    session: Session = Depends(get_session),
    user: AuthUser = Depends(require_contributor),
) -> SourceSubmission:
    """Propose a source for an article and enqueue it for review. Contributor role required."""
    submission = create_source_submission(session, slug, payload, user)
    if submission is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return submission


@app.get("/api/v1/contributors/overview", response_model=ContributorOverview)
def contributor_overview(
    session: Session = Depends(get_session),
    user: AuthUser = Depends(require_contributor),
) -> ContributorOverview:
    """Return suggestions and source submissions for the authenticated contributor."""
    return get_contributor_overview(session, user.email)


@app.get("/api/v1/reviews/queue", response_model=list[ReviewQueueItem])
def review_queue(
    status: str | None = Query(default=None),
    subject_type: str | None = Query(default=None),
    session: Session = Depends(get_session),
    _: AuthUser = Depends(require_reviewer),
) -> list[ReviewQueueItem]:
    """List review-queue items. Reviewer role required. Filter with `status` and `subject_type`."""
    return list_review_queue(session, status, subject_type)


@app.get("/api/v1/reviews/overview", response_model=ReviewerOverview)
def reviewer_overview(
    status: str | None = Query(default=None),
    subject_type: str | None = Query(default=None),
    session: Session = Depends(get_session),
    _: AuthUser = Depends(require_reviewer),
) -> ReviewerOverview:
    """Return queue counts and items for the reviewer dashboard. Reviewer role required."""
    return review_queue_overview(session, status, subject_type)


@app.post("/api/v1/reviews/queue/{queue_item_id}/assign", response_model=ReviewAssignment)
def assign_review_item(
    queue_item_id: str,
    session: Session = Depends(get_session),
    user: AuthUser = Depends(require_reviewer),
) -> ReviewAssignment:
    """Assign a queue item to the authenticated reviewer. Reviewer role required."""
    try:
        assignment = assign_review_queue_item(session, queue_item_id, user)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
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
    """Approve or reject a queue item with optional notes. Reviewer role required."""
    try:
        decision = create_review_decision(session, queue_item_id, payload, user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if decision is None:
        raise HTTPException(status_code=404, detail="Queue item not found")
    return decision


# --- Epistemic database endpoints ---


@app.get("/api/v1/articles/{slug}/claims", response_model=list[Claim])
def article_claims(slug: str, session: Session = Depends(get_session)) -> list[Claim]:
    """List atomic claims for an article, including per-claim confidence and citations."""
    claims = get_claims_by_article(session, slug)
    if claims is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return claims


@app.get("/api/v1/claims/{claim_id}", response_model=Claim)
def claim_detail(claim_id: str, session: Session = Depends(get_session)) -> Claim:
    """Return one claim and its citation chain."""
    claim = get_claim_by_id(session, claim_id)
    if claim is None:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@app.get("/api/v1/entities", response_model=list[Entity])
def get_entities(session: Session = Depends(get_session)) -> list[Entity]:
    """List knowledge-graph entities."""
    return list_entities(session)


@app.get("/api/v1/entities/{slug}", response_model=EntityGraph)
def entity_graph(slug: str, session: Session = Depends(get_session)) -> EntityGraph:
    """Return an entity, its outgoing and incoming relationships, and linked article slugs."""
    graph = get_entity_graph(session, slug)
    if graph is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return graph


@app.get("/api/v1/articles/{slug}/jsonld")
def article_jsonld(slug: str, session: Session = Depends(get_session)) -> JSONResponse:
    """Return the article as Schema.org JSON-LD. Content-Type is application/ld+json."""
    article = get_article_by_slug(session, slug)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return JSONResponse(content=build_jsonld_article(article), media_type="application/ld+json")


@app.get("/api/v1/export", dependencies=[Depends(limit_export)])
def export_knowledge(
    format: str = Query(default="jsonld", pattern="^(jsonld)$"),
    session: Session = Depends(get_session),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> JSONResponse:
    """Export one bounded page of the knowledge graph as JSON-LD."""
    all_articles = list_articles(session)
    all_entities = list_entities(session)
    payload = build_jsonld_export(all_articles, all_entities)
    graph = payload["@graph"]
    total = len(graph)
    payload["@graph"] = graph[offset : offset + limit]
    headers = {"X-Total-Count": str(total)}
    if offset + limit < total:
        next_offset = offset + limit
        headers["Link"] = (
            f'</api/v1/export?format=jsonld&limit={limit}&offset={next_offset}>; rel="next"'
        )
    return JSONResponse(content=payload, headers=headers, media_type="application/ld+json")
