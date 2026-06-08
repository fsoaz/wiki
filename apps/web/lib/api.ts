import { cookies } from "next/headers";
import { fallbackArticles, fallbackSearch } from "@/lib/mock";
import type {
  AdminOverview,
  Article,
  ArticleChatResponse,
  AuthSessionInfo,
  AuthUser,
  ContributorOverview,
  ReviewAssignment,
  ReviewerOverview,
  SearchResult
} from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function safeFetch<T>(path: string, init?: RequestInit): Promise<T | null> {
  try {
    const response = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: await buildAuthHeaders(init?.headers),
      cache: "no-store"
    });
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

async function buildAuthHeaders(existingHeaders?: HeadersInit): Promise<Record<string, string>> {
  const cookieStore = await cookies();
  const token = cookieStore.get("wikiai_token")?.value;

  const normalized: Record<string, string> = {
    "Content-Type": "application/json"
  };

  if (existingHeaders instanceof Headers) {
    existingHeaders.forEach((value, key) => {
      normalized[key] = value;
    });
  } else if (Array.isArray(existingHeaders)) {
    for (const [key, value] of existingHeaders) {
      normalized[key] = value;
    }
  } else if (existingHeaders) {
    Object.assign(normalized, existingHeaders);
  }

  if (token) {
    normalized.Authorization = `Bearer ${token}`;
  }

  return normalized;
}

export async function getFeaturedArticles(): Promise<Article[]> {
  const data = await safeFetch<Article[]>("/api/v1/articles");
  return data ?? fallbackArticles;
}

export async function getArticle(slug: string): Promise<Article | null> {
  const data = await safeFetch<Article>(`/api/v1/articles/${slug}`);
  return data ?? fallbackArticles.find((article) => article.slug === slug) ?? null;
}

export async function searchKnowledge(query: string): Promise<SearchResult> {
  const encodedQuery = encodeURIComponent(query);
  const data = await safeFetch<SearchResult>(`/api/v1/search?q=${encodedQuery}`);
  return data ?? fallbackSearch;
}

export async function askArticle(slug: string, question: string): Promise<ArticleChatResponse | null> {
  return safeFetch<ArticleChatResponse>(`/api/v1/articles/${slug}/chat`, {
    method: "POST",
    body: JSON.stringify({ question })
  });
}

export async function getContributorOverview(): Promise<ContributorOverview | null> {
  return safeFetch<ContributorOverview>("/api/v1/contributors/overview");
}

export async function getReviewerOverview(status?: string, subjectType?: string): Promise<ReviewerOverview | null> {
  const params = new URLSearchParams();
  if (status) params.set("status", status);
  if (subjectType) params.set("subject_type", subjectType);
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return safeFetch<ReviewerOverview>(`/api/v1/reviews/overview${suffix}`);
}

export async function getAuthSession(): Promise<AuthUser | null> {
  return safeFetch<AuthUser>("/api/v1/auth/session");
}

export async function getAdminOverview(): Promise<AdminOverview | null> {
  return safeFetch<AdminOverview>("/api/v1/admin/overview");
}

export async function getAdminSessions(): Promise<AuthSessionInfo[] | null> {
  return safeFetch<AuthSessionInfo[]>("/api/v1/admin/sessions");
}

export async function submitArticleSuggestion(
  slug: string,
  payload: {
    suggestion_type: "edit" | "source" | "outdated" | "correction";
    summary: string;
    proposed_text?: string;
    source_url?: string;
  }
): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/api/v1/articles/${slug}/suggestions`, {
      method: "POST",
      headers: await buildAuthHeaders(),
      body: JSON.stringify(payload),
      cache: "no-store"
    });
    return response.ok;
  } catch {
    return false;
  }
}

export async function submitArticleSource(
  slug: string,
  payload: {
    title: string;
    publisher: string;
    url: string;
    rationale: string;
  }
): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/api/v1/articles/${slug}/sources`, {
      method: "POST",
      headers: await buildAuthHeaders(),
      body: JSON.stringify(payload),
      cache: "no-store"
    });
    return response.ok;
  } catch {
    return false;
  }
}

export async function submitReviewDecision(
  queueItemId: string,
  payload: {
    decision: "approved" | "rejected";
    notes?: string;
  }
): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/api/v1/reviews/queue/${queueItemId}/decision`, {
      method: "POST",
      headers: await buildAuthHeaders(),
      body: JSON.stringify(payload),
      cache: "no-store"
    });
    return response.ok;
  } catch {
    return false;
  }
}

export async function assignReviewItem(queueItemId: string): Promise<ReviewAssignment | null> {
  try {
    const response = await fetch(`${API_URL}/api/v1/reviews/queue/${queueItemId}/assign`, {
      method: "POST",
      headers: await buildAuthHeaders(),
      cache: "no-store"
    });
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as ReviewAssignment;
  } catch {
    return null;
  }
}

export async function revokeAdminSession(sessionId: string): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/api/v1/admin/sessions/${sessionId}/revoke`, {
      method: "POST",
      headers: await buildAuthHeaders(),
      cache: "no-store"
    });
    return response.ok && (await response.json()).ok === true;
  } catch {
    return false;
  }
}
