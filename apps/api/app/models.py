from datetime import date
from typing import Literal

from pydantic import BaseModel


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
    question: str


class ChatResponse(BaseModel):
    answer: str
    confidence_score: float
    citations: list[Source]
    reasoning: list[str]


class ArticleSuggestionCreate(BaseModel):
    suggestion_type: Literal["edit", "source", "outdated", "correction"] = "edit"
    summary: str
    proposed_text: str | None = None
    source_url: str | None = None


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


class SourceSubmissionCreate(BaseModel):
    title: str
    publisher: str
    url: str
    rationale: str


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
    notes: str | None = None


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
    email: str


class AuthSession(BaseModel):
    token: str
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
    created_at: str
