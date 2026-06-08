import { ArrowRight, ShieldCheck, Sparkles, TimerReset } from "lucide-react";
import { SiteHeader } from "@/components/site-header";
import { Badge, ButtonLink, Panel } from "@/components/ui";
import { getFeaturedArticles } from "@/lib/api";

export default async function HomePage() {
  const articles = await getFeaturedArticles();

  return (
    <main className="min-h-screen pb-16">
      <SiteHeader />
      <section className="mx-auto grid max-w-7xl gap-8 px-6 pb-8 pt-6 lg:grid-cols-[1.25fr_0.75fr] lg:px-10">
        <div className="space-y-8">
          <Badge>Wikipedia 2.0 MVP</Badge>
          <div className="space-y-6">
            <h1 className="max-w-4xl font-serif text-5xl leading-[0.95] tracking-tight md:text-7xl">
              The most transparent way to ask for knowledge.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-black/72">
              WikiAI combines canonical articles, claim-level citations, verification dates, and grounded AI
              answers in one trust-centric interface.
            </p>
          </div>
          <div className="flex flex-wrap gap-4">
            <ButtonLink href="/search?q=explain%20quantum%20computing%20for%20beginners">
              Explore AI search
            </ButtonLink>
            <ButtonLink href="/articles/quantum-computing" variant="secondary">
              Open a sample article
            </ButtonLink>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            {[
              {
                icon: ShieldCheck,
                title: "Verifiable",
                body: "Every featured article surfaces sources, confidence, and last verification date."
              },
              {
                icon: Sparkles,
                title: "AI-assisted",
                body: "Search answers and summaries are grounded in reviewed evidence, not freeform generation."
              },
              {
                icon: TimerReset,
                title: "Continuously updated",
                body: "The architecture is prepared for source monitoring and revision proposals."
              }
            ].map(({ icon: Icon, title, body }) => (
              <Panel key={title} className="p-5">
                <Icon className="mb-4 h-5 w-5 text-accent" />
                <h2 className="text-sm font-semibold uppercase tracking-[0.16em] text-black/70">{title}</h2>
                <p className="mt-3 text-sm leading-6 text-black/70">{body}</p>
              </Panel>
            ))}
          </div>
        </div>
        <Panel className="overflow-hidden">
          <div className="border-b border-black/10 p-6">
            <div className="text-xs uppercase tracking-[0.22em] text-black/55">Featured topics</div>
            <div className="mt-2 font-serif text-3xl">Canonical article set</div>
          </div>
          <div className="space-y-4 p-6">
            {articles.map((article) => (
              <a
                key={article.slug}
                href={`/articles/${article.slug}`}
                className="block rounded-[1.5rem] border border-black/10 bg-mist/80 p-5 transition-colors hover:bg-white"
              >
                <div className="flex items-center justify-between gap-4">
                  <h2 className="font-serif text-2xl">{article.title}</h2>
                  <ArrowRight className="h-4 w-4 text-black/50" />
                </div>
                <p className="mt-3 text-sm leading-6 text-black/70">{article.summary}</p>
                <div className="mt-4 flex flex-wrap gap-2 text-xs uppercase tracking-[0.16em] text-black/55">
                  <span>Confidence {Math.round(article.confidence_score * 100)}%</span>
                  <span>Verified {article.last_verified_at}</span>
                </div>
              </a>
            ))}
          </div>
        </Panel>
      </section>
      <section className="mx-auto mt-10 max-w-7xl px-6 lg:px-10">
        <Panel className="grid gap-6 p-8 lg:grid-cols-3">
          <div>
            <div className="text-xs uppercase tracking-[0.22em] text-black/55">MVP scope</div>
            <h2 className="mt-3 font-serif text-3xl">A narrow, real foundation</h2>
          </div>
          <div className="text-sm leading-7 text-black/72">
            This first implementation includes a FastAPI knowledge API, seeded article data, AI search results with
            citations, and a Next.js surface for article reading.
          </div>
          <div className="text-sm leading-7 text-black/72">
            The database schema, Docker wiring, and event-oriented architecture are laid down so the project can move
            from demo data to production infrastructure without rewriting the contract.
          </div>
        </Panel>
      </section>
    </main>
  );
}

