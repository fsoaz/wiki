CREATE TABLE users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    auth_provider TEXT NOT NULL DEFAULT 'password',
    display_name TEXT NOT NULL,
    role TEXT NOT NULL,
    reputation_score NUMERIC(5,2) NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active',
    locale TEXT NOT NULL DEFAULT 'en',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE auth_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    expertise_areas TEXT[] NOT NULL DEFAULT '{}',
    verification_level TEXT,
    organization TEXT,
    country TEXT
);

CREATE TABLE expert_verifications (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    credential_type TEXT NOT NULL,
    issuer TEXT NOT NULL,
    credential_reference TEXT NOT NULL,
    status TEXT NOT NULL,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ
);

CREATE TABLE articles (
    id UUID PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    primary_language TEXT NOT NULL DEFAULT 'en',
    current_revision_id UUID,
    canonical_summary_revision_id UUID,
    current_confidence_score NUMERIC(4,3),
    last_verified_at TIMESTAMPTZ,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE revisions (
    id UUID PRIMARY KEY,
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    revision_number INTEGER NOT NULL,
    author_type TEXT NOT NULL,
    author_user_id UUID REFERENCES users(id),
    source_revision_parent_id UUID REFERENCES revisions(id),
    change_summary TEXT NOT NULL,
    status TEXT NOT NULL,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(article_id, revision_number)
);

ALTER TABLE articles
    ADD CONSTRAINT fk_current_revision
    FOREIGN KEY (current_revision_id)
    REFERENCES revisions(id);

ALTER TABLE articles
    ADD CONSTRAINT fk_summary_revision
    FOREIGN KEY (canonical_summary_revision_id)
    REFERENCES revisions(id);

CREATE TABLE article_sections (
    id UUID PRIMARY KEY,
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    revision_id UUID NOT NULL REFERENCES revisions(id) ON DELETE CASCADE,
    section_key TEXT NOT NULL,
    heading TEXT NOT NULL,
    content_md TEXT NOT NULL,
    position INTEGER NOT NULL
);

CREATE TABLE article_timelines (
    id UUID PRIMARY KEY,
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    revision_id UUID NOT NULL REFERENCES revisions(id) ON DELETE CASCADE,
    event_date TEXT NOT NULL,
    event_label TEXT NOT NULL,
    event_description TEXT NOT NULL,
    position INTEGER NOT NULL
);

CREATE TABLE article_related_topics (
    id UUID PRIMARY KEY,
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    UNIQUE (article_id, topic)
);

CREATE TABLE article_relationships (
    id UUID PRIMARY KEY,
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    related_article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL,
    strength_score NUMERIC(4,3) NOT NULL
);

CREATE TABLE categories (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    parent_id UUID REFERENCES categories(id)
);

CREATE TABLE article_categories (
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    category_id UUID NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (article_id, category_id)
);

CREATE TABLE tags (
    id UUID PRIMARY KEY,
    label TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL
);

CREATE TABLE article_tags (
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (article_id, tag_id)
);

CREATE TABLE revision_diffs (
    id UUID PRIMARY KEY,
    revision_id UUID NOT NULL UNIQUE REFERENCES revisions(id) ON DELETE CASCADE,
    diff_json JSONB NOT NULL,
    rendered_diff_md TEXT NOT NULL
);

CREATE TABLE claims (
    id UUID PRIMARY KEY,
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    revision_id UUID NOT NULL REFERENCES revisions(id) ON DELETE CASCADE,
    claim_text TEXT NOT NULL,
    claim_type TEXT NOT NULL,
    section_key TEXT NOT NULL,
    claim_hash TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE sources (
    id UUID PRIMARY KEY,
    source_type TEXT NOT NULL,
    title TEXT NOT NULL,
    publisher TEXT NOT NULL,
    authors_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    publication_date DATE,
    url TEXT NOT NULL,
    doi TEXT,
    language TEXT NOT NULL DEFAULT 'en',
    tier TEXT NOT NULL,
    credibility_score NUMERIC(4,3),
    freshness_score NUMERIC(4,3),
    retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE source_artifacts (
    id UUID PRIMARY KEY,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    artifact_type TEXT NOT NULL,
    storage_uri TEXT NOT NULL,
    checksum TEXT NOT NULL,
    parsed_text_version TEXT NOT NULL,
    extracted_metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE citations (
    id UUID PRIMARY KEY,
    claim_id UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    evidence_span TEXT NOT NULL,
    support_type TEXT NOT NULL,
    weight NUMERIC(4,3) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE verification_records (
    id UUID PRIMARY KEY,
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    revision_id UUID NOT NULL REFERENCES revisions(id) ON DELETE CASCADE,
    verification_run_id UUID NOT NULL,
    result TEXT NOT NULL,
    verified_at TIMESTAMPTZ NOT NULL,
    verified_by_type TEXT NOT NULL,
    verified_by_user_id UUID REFERENCES users(id)
);

CREATE TABLE contradictions (
    id UUID PRIMARY KEY,
    claim_id UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    contradiction_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    details_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL
);

CREATE TABLE confidence_metrics (
    id UUID PRIMARY KEY,
    subject_type TEXT NOT NULL,
    subject_id UUID NOT NULL,
    overall_score NUMERIC(4,3) NOT NULL,
    source_quality_score NUMERIC(4,3) NOT NULL,
    cross_source_agreement_score NUMERIC(4,3) NOT NULL,
    freshness_score NUMERIC(4,3) NOT NULL,
    coverage_score NUMERIC(4,3) NOT NULL,
    human_review_score NUMERIC(4,3) NOT NULL,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ai_conversations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    article_id UUID REFERENCES articles(id),
    query TEXT NOT NULL,
    response_text TEXT NOT NULL,
    grounding_status TEXT NOT NULL,
    confidence_score NUMERIC(4,3) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE article_suggestions (
    id UUID PRIMARY KEY,
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    contributor_name TEXT NOT NULL,
    contributor_email TEXT,
    suggestion_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    proposed_text TEXT,
    source_url TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE article_source_submissions (
    id UUID PRIMARY KEY,
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    contributor_name TEXT NOT NULL,
    contributor_email TEXT,
    title TEXT NOT NULL,
    publisher TEXT NOT NULL,
    url TEXT NOT NULL,
    rationale TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ai_answer_citations (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES ai_conversations(id) ON DELETE CASCADE,
    claim_id UUID REFERENCES claims(id),
    source_id UUID NOT NULL REFERENCES sources(id),
    span_reference TEXT NOT NULL,
    order_index INTEGER NOT NULL
);

CREATE TABLE verification_jobs (
    id UUID PRIMARY KEY,
    subject_type TEXT NOT NULL,
    subject_id UUID NOT NULL,
    trigger_type TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE TABLE review_queue_items (
    id UUID PRIMARY KEY,
    article_id UUID NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    subject_type TEXT NOT NULL,
    subject_id UUID NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    assigned_reviewer_email TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE review_decisions (
    id UUID PRIMARY KEY,
    queue_item_id UUID NOT NULL REFERENCES review_queue_items(id) ON DELETE CASCADE,
    reviewer_email TEXT NOT NULL,
    decision TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    actor_email TEXT,
    actor_role TEXT,
    action TEXT NOT NULL,
    subject_type TEXT NOT NULL,
    subject_id UUID,
    details_json TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE moderation_events (
    id UUID PRIMARY KEY,
    target_type TEXT NOT NULL,
    target_id UUID NOT NULL,
    policy_code TEXT NOT NULL,
    action_taken TEXT NOT NULL,
    reviewer_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
