from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


Tier = Literal["A", "B", "C", "D"]


class Source(BaseModel):
    id: str
    title: str
    publisher: str
    tier: Tier
    url: str
    published_at: date


class TimelineEvent(BaseModel):
    date: str
    title: str
    description: str


class ArticleSection(BaseModel):
    heading: str
    content: str
    citations: list[str]


class ArticleSummary(BaseModel):
    slug: str
    title: str
    summary: str
    confidence_score: float
    last_verified_at: date


class Article(ArticleSummary):
    verification_status: str
    related_topics: list[str]
    sections: list[ArticleSection]
    timeline: list[TimelineEvent]
    sources: list[Source]
    revision_count: int


class SearchResponse(BaseModel):
    answer: str
    confidence_score: float
    sources: list[Source]
    articles: list[ArticleSummary]


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2_000)

    @field_validator("question")
    @classmethod
    def question_must_have_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("question must not be blank")
        return value.strip()


class ChatResponse(BaseModel):
    answer: str
    confidence_score: float
    citations: list[Source]
    reasoning: list[str]


class ArticleSuggestionCreate(BaseModel):
    suggestion_type: Literal["edit", "source", "outdated", "correction"] = "edit"
    summary: str = Field(min_length=1, max_length=500)
    proposed_text: str | None = Field(default=None, max_length=10_000)
    source_url: str | None = Field(default=None, max_length=2_048)

    @field_validator("summary")
    @classmethod
    def summary_must_have_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("summary must not be blank")
        return value.strip()


class ArticleSuggestion(BaseModel):
    id: str
    article_slug: str
    contributor_name: str
    contributor_email: str | None = None
    suggestion_type: str
    summary: str
    proposed_text: str | None = None
    source_url: str | None = None
    status: str
    created_at: str


class PublicArticleSuggestion(BaseModel):
    id: str
    article_slug: str
    contributor_name: str
    suggestion_type: str
    summary: str
    proposed_text: str | None = None
    source_url: str | None = None
    status: str
    created_at: str


class SourceSubmissionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    publisher: str = Field(min_length=1, max_length=255)
    url: str = Field(min_length=1, max_length=2_048)
    rationale: str = Field(min_length=1, max_length=2_000)

    @field_validator("title", "publisher", "url", "rationale")
    @classmethod
    def fields_must_have_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field must not be blank")
        return value.strip()


class SourceSubmission(BaseModel):
    id: str
    article_slug: str
    contributor_name: str
    contributor_email: str | None = None
    title: str
    publisher: str
    url: str
    rationale: str
    status: str
    created_at: str


class ContributorOverview(BaseModel):
    contributor_email: str
    suggestion_count: int
    source_submission_count: int
    suggestions: list[ArticleSuggestion]
    source_submissions: list[SourceSubmission]


class ReviewQueueItem(BaseModel):
    id: str
    article_slug: str
    article_title: str
    subject_type: Literal["suggestion", "source_submission"]
    subject_id: str
    priority: str
    status: str
    assigned_reviewer_email: str | None = None
    summary: str
    contributor_name: str
    contributor_email: str | None = None
    created_at: str
    decisions: list["ReviewDecision"] = []


class ReviewDecisionCreate(BaseModel):
    decision: Literal["approved", "rejected"]
    notes: str | None = Field(default=None, max_length=2_000)


class ReviewDecision(BaseModel):
    id: str
    queue_item_id: str
    reviewer_email: str
    decision: str
    notes: str | None = None
    created_at: str


class ReviewAssignment(BaseModel):
    queue_item_id: str
    assigned_reviewer_email: str
    status: str


class ReviewerOverview(BaseModel):
    pending_count: int
    approved_count: int
    rejected_count: int
    items: list[ReviewQueueItem]


Role = Literal["contributor", "reviewer", "admin"]


class AuthUser(BaseModel):
    id: str
    email: str
    display_name: str
    role: Role


class AuthLoginRequest(BaseModel):
    email: str = Field(max_length=254)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class AuthSession(BaseModel):
    token: str
    expires_at: str
    user: AuthUser


class AuditLogEntry(BaseModel):
    id: str
    actor_email: str | None = None
    actor_role: str | None = None
    action: str
    subject_type: str
    subject_id: str | None = None
    details_json: str | None = None
    created_at: str


class AdminOverview(BaseModel):
    audit_event_count: int
    review_queue_count: int
    active_session_count: int
    recent_audit_entries: list[AuditLogEntry]


class AuthSessionInfo(BaseModel):
    id: str
    user_email: str
    user_role: str
    expires_at: str
    created_at: str


class ClaimCitation(BaseModel):
    id: str
    source_id: str
    evidence_span: str
    support_type: str


class ConfidenceMetrics(BaseModel):
    id: str
    subject_type: str
    subject_id: str
    overall_score: float
    source_quality_score: float
    cross_source_agreement_score: float
    freshness_score: float
    coverage_score: float
    human_review_score: float
    computed_at: str


class Contradiction(BaseModel):
    id: str
    claim_id: str
    source_id: str
    contradiction_type: str
    severity: str
    details_json: str
    status: str


class Claim(BaseModel):
    id: str
    article_slug: str
    claim_text: str
    claim_type: str
    section_key: str
    status: str
    confidence: float
    citations: list[ClaimCitation] = []
    confidence_metrics: ConfidenceMetrics | None = None
    contradictions: list[Contradiction] = []


class Entity(BaseModel):
    id: str
    name: str
    entity_type: str
    canonical_slug: str
    description: str


class EntityRelationship(BaseModel):
    id: str
    subject_slug: str
    subject_name: str
    predicate: str
    object_slug: str
    object_name: str
    confidence: float


class EntityGraph(BaseModel):
    entity: Entity
    relationships: list[EntityRelationship]
    article_slugs: list[str]
