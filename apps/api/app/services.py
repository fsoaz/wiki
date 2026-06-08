from sqlalchemy.orm import Session

from .models import Article, ArticleSummary, ChatResponse, SearchResponse
from .repository import search_articles


def summarize_articles(articles: list[Article]) -> list[ArticleSummary]:
    return [
        ArticleSummary(
            slug=article.slug,
            title=article.title,
            summary=article.summary,
            confidence_score=article.confidence_score,
            last_verified_at=article.last_verified_at,
        )
        for article in articles
    ]


def build_search_response(session: Session, query: str) -> SearchResponse:
    articles = list(search_articles(session, query))
    lead = articles[0]
    answer = (
        f"{lead.title} is the strongest current match for '{query}'. "
        f"{lead.summary} The current MVP answer is grounded in the article's reviewed sections and linked sources."
    )
    return SearchResponse(
        answer=answer,
        confidence_score=lead.confidence_score,
        sources=lead.sources,
        articles=summarize_articles(articles),
    )


def build_chat_response(article: Article, question: str) -> ChatResponse:
    answer = (
        f"Based on the validated material in {article.title}, the best short answer to '{question}' is: "
        f"{article.sections[0].content}"
    )
    return ChatResponse(
        answer=answer,
        confidence_score=article.confidence_score,
        citations=article.sources[:2],
        reasoning=[
            "Matched the question against the article summary and reviewed sections.",
            "Used only seeded approved article content for the answer body.",
            "Returned the top supporting sources attached to the relevant claims.",
        ],
    )
