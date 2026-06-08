export type Source = {
  id: string;
  title: string;
  publisher: string;
  tier: "A" | "B" | "C" | "D";
  url: string;
  published_at: string;
};

export type TimelineEvent = {
  date: string;
  title: string;
  description: string;
};

export type ArticleSection = {
  heading: string;
  content: string;
  citations: string[];
};

export type Article = {
  slug: string;
  title: string;
  summary: string;
  confidence_score: number;
  verification_status: string;
  last_verified_at: string;
  related_topics: string[];
  sections: ArticleSection[];
  timeline: TimelineEvent[];
  sources: Source[];
  revision_count: number;
};

export type SearchResult = {
  answer: string;
  confidence_score: number;
  sources: Source[];
  articles: Pick<Article, "slug" | "title" | "summary" | "confidence_score" | "last_verified_at">[];
};

export type ArticleChatResponse = {
  answer: string;
  confidence_score: number;
  citations: Source[];
  reasoning: string[];
};

export type ArticleSuggestion = {
  id: string;
  article_slug: string;
  contributor_name: string;
  contributor_email?: string | null;
  suggestion_type: string;
  summary: string;
  proposed_text?: string | null;
  source_url?: string | null;
  status: string;
  created_at: string;
};

export type SourceSubmission = {
  id: string;
  article_slug: string;
  contributor_name: string;
  contributor_email?: string | null;
  title: string;
  publisher: string;
  url: string;
  rationale: string;
  status: string;
  created_at: string;
};

export type ContributorOverview = {
  contributor_email: string;
  suggestion_count: number;
  source_submission_count: number;
  suggestions: ArticleSuggestion[];
  source_submissions: SourceSubmission[];
};

export type ReviewQueueItem = {
  id: string;
  article_slug: string;
  article_title: string;
  subject_type: "suggestion" | "source_submission";
  subject_id: string;
  priority: string;
  status: string;
  assigned_reviewer_email?: string | null;
  summary: string;
  contributor_name: string;
  contributor_email?: string | null;
  created_at: string;
  decisions: ReviewDecision[];
};

export type ReviewerOverview = {
  pending_count: number;
  approved_count: number;
  rejected_count: number;
  items: ReviewQueueItem[];
};

export type ReviewDecision = {
  id: string;
  queue_item_id: string;
  reviewer_email: string;
  decision: string;
  notes?: string | null;
  created_at: string;
};

export type ReviewAssignment = {
  queue_item_id: string;
  assigned_reviewer_email: string;
  status: string;
};

export type AuthUser = {
  id: string;
  email: string;
  display_name: string;
  role: "contributor" | "reviewer" | "admin";
};

export type AuditLogEntry = {
  id: string;
  actor_email?: string | null;
  actor_role?: string | null;
  action: string;
  subject_type: string;
  subject_id?: string | null;
  details_json?: string | null;
  created_at: string;
};

export type AdminOverview = {
  audit_event_count: number;
  review_queue_count: number;
  active_session_count: number;
  recent_audit_entries: AuditLogEntry[];
};

export type AuthSessionInfo = {
  id: string;
  user_email: string;
  user_role: string;
  created_at: string;
};
