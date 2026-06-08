import { revalidatePath } from "next/cache";
import { notFound, redirect } from "next/navigation";
import { SiteHeader } from "@/components/site-header";
import { Badge, Panel } from "@/components/ui";
import { getArticle, getAuthSession, submitArticleSource, submitArticleSuggestion } from "@/lib/api";

export default async function ArticlePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const article = await getArticle(slug);
  const user = await getAuthSession();

  if (!article) {
    notFound();
  }

  async function submitSuggestionAction(formData: FormData) {
    "use server";

    const summary = String(formData.get("summary") ?? "");
    const proposedText = String(formData.get("proposed_text") ?? "");
    const sourceUrl = String(formData.get("source_url") ?? "");

    const ok = await submitArticleSuggestion(slug, {
      suggestion_type: "edit",
      summary,
      proposed_text: proposedText || undefined,
      source_url: sourceUrl || undefined,
    });

    if (!ok) {
      redirect(`/signin?next=/articles/${slug}`);
    }

    revalidatePath(`/articles/${slug}`);
    redirect(`/contributors`);
  }

  async function submitSourceAction(formData: FormData) {
    "use server";

    const title = String(formData.get("title") ?? "");
    const publisher = String(formData.get("publisher") ?? "");
    const url = String(formData.get("url") ?? "");
    const rationale = String(formData.get("rationale") ?? "");

    const ok = await submitArticleSource(slug, { title, publisher, url, rationale });
    if (!ok) {
      redirect(`/signin?next=/articles/${slug}`);
    }

    revalidatePath(`/articles/${slug}`);
    redirect(`/contributors`);
  }

  return (
    <main className="min-h-screen pb-16">
      <SiteHeader />
      <section className="mx-auto max-w-7xl px-6 py-8 lg:px-10">
        <div className="grid gap-8 lg:grid-cols-[0.8fr_1.4fr_0.8fr]">
          <aside className="space-y-3">
            <div className="text-xs uppercase tracking-[0.22em] text-black/55">Sections</div>
            {article.sections.map((section) => (
              <a key={section.heading} href={`#${section.heading.toLowerCase().replaceAll(" ", "-")}`} className="block text-sm text-black/65 hover:text-black">
                {section.heading}
              </a>
            ))}
          </aside>
          <article className="space-y-6">
            <div className="space-y-4">
              <Badge>{article.verification_status}</Badge>
              <h1 className="font-serif text-5xl tracking-tight">{article.title}</h1>
              <p className="max-w-3xl text-lg leading-8 text-black/72">{article.summary}</p>
              <div className="flex flex-wrap gap-3 text-xs uppercase tracking-[0.16em] text-black/55">
                <span>Confidence {Math.round(article.confidence_score * 100)}%</span>
                <span>Verified {article.last_verified_at}</span>
                <span>{article.revision_count} revisions</span>
              </div>
            </div>
            {article.sections.map((section) => (
              <Panel key={section.heading} className="p-6" >
                <section id={section.heading.toLowerCase().replaceAll(" ", "-")}>
                  <h2 className="font-serif text-3xl">{section.heading}</h2>
                  <p className="mt-4 text-base leading-8 text-black/74">{section.content}</p>
                  <div className="mt-4 flex flex-wrap gap-2 text-xs uppercase tracking-[0.16em] text-black/55">
                    {section.citations.map((citation) => (
                      <span key={citation}>Citation {citation}</span>
                    ))}
                  </div>
                </section>
              </Panel>
            ))}
          </article>
          <aside className="space-y-5">
            <Panel className="p-5">
              <div className="text-xs uppercase tracking-[0.22em] text-black/55">Related topics</div>
              <div className="mt-3 flex flex-wrap gap-2">
                {article.related_topics.map((topic) => (
                  <Badge key={topic} className="bg-mist">{topic}</Badge>
                ))}
              </div>
            </Panel>
            <Panel className="p-5">
              <div className="text-xs uppercase tracking-[0.22em] text-black/55">Timeline</div>
              <div className="mt-4 space-y-4">
                {article.timeline.map((event) => (
                  <div key={`${event.date}-${event.title}`} className="border-l border-black/10 pl-4">
                    <div className="text-xs uppercase tracking-[0.16em] text-black/50">{event.date}</div>
                    <div className="mt-1 font-medium">{event.title}</div>
                    <div className="mt-1 text-sm leading-6 text-black/68">{event.description}</div>
                  </div>
                ))}
              </div>
            </Panel>
            <Panel className="p-5">
              <div className="text-xs uppercase tracking-[0.22em] text-black/55">Sources</div>
              <div className="mt-4 space-y-3">
                {article.sources.map((source) => (
                  <a key={source.id} href={source.url} className="block rounded-2xl border border-black/10 bg-mist/80 p-4 hover:bg-white">
                    <div className="flex items-center justify-between gap-3">
                      <span className="font-medium">{source.publisher}</span>
                      <span className="text-xs uppercase tracking-[0.16em] text-black/50">Tier {source.tier}</span>
                    </div>
                    <div className="mt-2 text-sm leading-6 text-black/70">{source.title}</div>
                  </a>
                ))}
              </div>
            </Panel>
            <Panel className="p-5">
              <div className="text-xs uppercase tracking-[0.22em] text-black/55">Contribute</div>
              {user ? (
                <div className="mt-4 space-y-5">
                  <form action={submitSuggestionAction} className="space-y-3">
                    <div className="text-sm font-medium">Suggest an article improvement</div>
                    <textarea
                      name="summary"
                      required
                      placeholder="Describe the edit you want reviewed."
                      className="min-h-24 w-full rounded-2xl border border-black/10 bg-white/80 px-4 py-3 text-sm outline-none"
                    />
                    <textarea
                      name="proposed_text"
                      placeholder="Optional proposed wording"
                      className="min-h-24 w-full rounded-2xl border border-black/10 bg-white/80 px-4 py-3 text-sm outline-none"
                    />
                    <input
                      name="source_url"
                      type="url"
                      placeholder="Optional supporting source URL"
                      className="w-full rounded-2xl border border-black/10 bg-white/80 px-4 py-3 text-sm outline-none"
                    />
                    <button className="rounded-full bg-ink px-4 py-2 text-sm font-semibold text-white" type="submit">
                      Submit suggestion
                    </button>
                  </form>
                  <form action={submitSourceAction} className="space-y-3 border-t border-black/10 pt-5">
                    <div className="text-sm font-medium">Submit a source</div>
                    <input
                      name="title"
                      required
                      placeholder="Source title"
                      className="w-full rounded-2xl border border-black/10 bg-white/80 px-4 py-3 text-sm outline-none"
                    />
                    <input
                      name="publisher"
                      required
                      placeholder="Publisher"
                      className="w-full rounded-2xl border border-black/10 bg-white/80 px-4 py-3 text-sm outline-none"
                    />
                    <input
                      name="url"
                      type="url"
                      required
                      placeholder="https://example.com/source"
                      className="w-full rounded-2xl border border-black/10 bg-white/80 px-4 py-3 text-sm outline-none"
                    />
                    <textarea
                      name="rationale"
                      required
                      placeholder="Why this source improves the article"
                      className="min-h-24 w-full rounded-2xl border border-black/10 bg-white/80 px-4 py-3 text-sm outline-none"
                    />
                    <button className="rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink" type="submit">
                      Submit source
                    </button>
                  </form>
                </div>
              ) : (
                <div className="mt-4 text-sm leading-6 text-black/68">
                  Sign in as a contributor to submit article improvements or new sources.
                  <div className="mt-3">
                    <a href={`/signin?next=/articles/${slug}`} className="text-accent hover:text-ink">
                      Go to sign in
                    </a>
                  </div>
                </div>
              )}
            </Panel>
          </aside>
        </div>
      </section>
    </main>
  );
}
