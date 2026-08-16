import json
import re
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from .db_models import (
    ArticleRecord,
    ClaimCitationRecord,
    ClaimRecord,
    ConfidenceMetricRecord,
    ContradictionRecord,
    SourceRecord,
)

TIER_SCORES = {"A": 0.95, "B": 0.85, "C": 0.70, "D": 0.50}
CONFIDENCE_AS_OF = date(2026, 8, 16)
NEGATION_TOKENS = {"not", "never", "no"}
_TOKEN_RE = re.compile(r"[a-z0-9]+")


def evidence_span_from_section(claim_text: str, section_content: str) -> str:
    if not section_content:
        return claim_text
    haystack = section_content.lower()
    needle = claim_text.lower().rstrip(".")
    idx = haystack.find(needle)
    if idx >= 0:
        return section_content[idx : idx + len(needle)]
    span = _longest_common_substring(claim_text, section_content)
    return span if span else claim_text


def _longest_common_substring(claim_text: str, section_content: str) -> str:
    a = claim_text.lower()
    b = section_content.lower()
    best_len = 0
    best_end_b = 0
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        current = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                current[j] = prev[j - 1] + 1
                if current[j] > best_len:
                    best_len = current[j]
                    best_end_b = j
        prev = current
    if best_len == 0:
        return ""
    return section_content[best_end_b - best_len : best_end_b]


def compute_claim_confidence(
    supporting_sources: list[tuple[str, date]],
    verification_status: str,
) -> dict[str, float]:
    supporting_count = len(supporting_sources)
    if supporting_count == 0:
        source_quality_score = 0.0
        freshness_score = 0.80
    else:
        source_quality_score = min(TIER_SCORES.get(tier, 0.50) for tier, _ in supporting_sources)
        newest = max(published_at for _, published_at in supporting_sources)
        freshness_score = 1.0 if (CONFIDENCE_AS_OF - newest).days <= 365 else 0.80
    return {
        "source_quality_score": source_quality_score,
        "cross_source_agreement_score": 1.0 if supporting_count >= 2 else 0.70,
        "freshness_score": freshness_score,
        "coverage_score": min(1.0, supporting_count / 2),
        "human_review_score": 1.0 if verification_status == "verified" else 0.50,
        "overall_score": source_quality_score,
    }


def persist_claim_confidence(session: Session, claim: ClaimRecord, article: ArticleRecord) -> None:
    supporting = [c for c in claim.citations if c.support_type == "supports"]
    source_ids = [c.source_id for c in supporting]
    sources: list[tuple[str, date]] = []
    if source_ids:
        records = session.scalars(select(SourceRecord).where(SourceRecord.id.in_(source_ids))).all()
        sources = [(r.tier, r.published_at) for r in records]
    scores = compute_claim_confidence(sources, article.verification_status)
    claim.confidence = scores["overall_score"]
    session.add(
        ConfidenceMetricRecord(
            subject_type="claim",
            subject_id=claim.id,
            overall_score=scores["overall_score"],
            source_quality_score=scores["source_quality_score"],
            cross_source_agreement_score=scores["cross_source_agreement_score"],
            freshness_score=scores["freshness_score"],
            coverage_score=scores["coverage_score"],
            human_review_score=scores["human_review_score"],
        )
    )


def _tokens(text: str) -> set[str]:
    return set(_TOKEN_RE.findall(text.lower()))


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _is_negation_pair(left: str, right: str) -> bool:
    left_has = bool(_tokens(left) & NEGATION_TOKENS)
    right_has = bool(_tokens(right) & NEGATION_TOKENS)
    return left_has != right_has


def detect_and_store_contradictions(session: Session, claim: ClaimRecord) -> None:
    for citation in claim.citations:
        if citation.support_type == "contradicts":
            session.add(
                ContradictionRecord(
                    claim_id=claim.id,
                    source_id=citation.source_id,
                    contradiction_type="source_conflict",
                    severity="medium",
                    details_json="{}",
                    status="open",
                )
            )

    others = session.scalars(
        select(ClaimRecord).where(
            ClaimRecord.article_id == claim.article_id,
            ClaimRecord.status == "active",
            ClaimRecord.id != claim.id,
        )
    ).all()
    claim_tokens = _tokens(claim.claim_text)
    supporting_ids = [c.source_id for c in claim.citations if c.support_type == "supports"]
    for other in others:
        if other.status != "active":
            continue
        if _jaccard(claim_tokens, _tokens(other.claim_text)) < 0.5:
            continue
        if not _is_negation_pair(claim.claim_text, other.claim_text):
            continue
        for source_id in supporting_ids:
            session.add(
                ContradictionRecord(
                    claim_id=claim.id,
                    source_id=source_id,
                    contradiction_type="claim_conflict",
                    severity="medium",
                    details_json=json.dumps({"conflicting_claim_id": other.id}),
                    status="open",
                )
            )
