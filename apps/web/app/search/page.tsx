import type { Route } from "next";
import Link from "next/link";
import { SiteHeader } from "@/components/site-header";
import { Badge, Panel } from "@/components/ui";
import { searchKnowledge } from "@/lib/api";

export default async function SearchPage({
  searchParams
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q = "explain quantum computing for beginners" } = await searchParams;
  const result = await searchKnowledge(q);

  return (
    <main className="min-h-screen pb-16">
      <SiteHeader />
      <section className="mx-auto max-w-7xl px-6 py-8 lg:px-10">
        <div className="mb-8 space-y-3">
          <div className="text-xs uppercase tracking-[0.22em] text-black/55">AI search</div>
          <h1 className="font-serif text-5xl tracking-tight">Results for “{q}”</h1>
        </div>
        <div className="grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
          <Panel className="p-6">
            <div className="flex items-center justify-between gap-4">
              <Badge>Grounded answer</Badge>
              <div className="text-xs uppercase tracking-[0.16em] text-black/55">
                Confidence {Math.round(result.confidence_score * 100)}%
              </div>
            </div>
            <p className="mt-5 text-lg leading-8 text-black/78">{result.answer}</p>
            <div className="mt-8 grid gap-3">
              {result.sources.map((source) => (
                <a key={source.id} href={source.url} className="rounded-[1.5rem] border border-black/10 bg-mist/70 p-4 hover:bg-white">
                  <div className="flex items-center justify-between gap-4">
                    <div className="font-medium">{source.publisher}</div>
                    <div className="text-xs uppercase tracking-[0.16em] text-black/50">Tier {source.tier}</div>
                  </div>
                  <div className="mt-1 text-sm leading-6 text-black/70">{source.title}</div>
                </a>
              ))}
            </div>
          </Panel>
          <div className="space-y-6">
            <Panel className="p-5">
              <div className="text-xs uppercase tracking-[0.22em] text-black/55">Canonical articles</div>
              <div className="mt-4 space-y-3">
                {result.articles.map((article) => (
                  <Link key={article.slug} href={`/articles/${article.slug}` as Route} className="block rounded-[1.5rem] border border-black/10 bg-white/70 p-4 hover:bg-white">
                    <div className="font-serif text-2xl">{article.title}</div>
                    <p className="mt-2 text-sm leading-6 text-black/70">{article.summary}</p>
                    <div className="mt-3 text-xs uppercase tracking-[0.16em] text-black/55">
                      Confidence {Math.round(article.confidence_score * 100)}% · Verified {article.last_verified_at}
                    </div>
                  </Link>
                ))}
              </div>
            </Panel>
            <Panel className="p-5">
              <div className="text-xs uppercase tracking-[0.22em] text-black/55">Follow-up prompts</div>
              <div className="mt-4 space-y-2 text-sm text-black/70">
                <div>How does error correction affect practical quantum systems?</div>
                <div>Which sources support the current consensus?</div>
                <div>Show a timeline of key breakthroughs.</div>
              </div>
            </Panel>
          </div>
        </div>
      </section>
    </main>
  );
}
