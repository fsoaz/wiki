import { redirect } from "next/navigation";
import { SiteHeader } from "@/components/site-header";
import { Badge, Panel } from "@/components/ui";
import { getAuthSession, getContributorOverview } from "@/lib/api";

export default async function ContributorsPage() {
  const user = await getAuthSession();
  if (!user) {
    redirect("/signin?next=/contributors");
  }

  const overview = await getContributorOverview();

  return (
    <main className="min-h-screen pb-16">
      <SiteHeader />
      <section className="mx-auto max-w-7xl px-6 py-8 lg:px-10">
        <div className="mb-8 space-y-3">
          <div className="text-xs uppercase tracking-[0.22em] text-black/55">Contributor dashboard</div>
          <h1 className="font-serif text-5xl tracking-tight">Contribution overview</h1>
          <p className="max-w-3xl text-base leading-7 text-black/72">
            Authenticated contributor view for your submitted suggestions and source proposals.
          </p>
        </div>
        <div className="mb-6 flex flex-wrap gap-3 text-sm text-black/70">
          <Badge>{user.email}</Badge>
          <Badge>{overview?.suggestion_count ?? 0} suggestions</Badge>
          <Badge>{overview?.source_submission_count ?? 0} source submissions</Badge>
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <Panel className="p-6">
            <div className="text-xs uppercase tracking-[0.22em] text-black/55">Edit suggestions</div>
            <div className="mt-4 space-y-3">
              {overview?.suggestions.length ? (
                overview.suggestions.map((suggestion) => (
                  <div key={suggestion.id} className="rounded-[1.5rem] border border-black/10 bg-mist/70 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div className="font-medium">{suggestion.article_slug}</div>
                      <Badge>{suggestion.status}</Badge>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-black/72">{suggestion.summary}</p>
                    {suggestion.proposed_text ? (
                      <p className="mt-3 text-sm leading-6 text-black/62">{suggestion.proposed_text}</p>
                    ) : null}
                  </div>
                ))
              ) : (
                <div className="rounded-[1.5rem] border border-dashed border-black/10 p-4 text-sm text-black/60">
                  No suggestions submitted yet for this contributor.
                </div>
              )}
            </div>
          </Panel>
          <Panel className="p-6">
            <div className="text-xs uppercase tracking-[0.22em] text-black/55">Source submissions</div>
            <div className="mt-4 space-y-3">
              {overview?.source_submissions.length ? (
                overview.source_submissions.map((submission) => (
                  <div key={submission.id} className="rounded-[1.5rem] border border-black/10 bg-white/70 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <div className="font-medium">{submission.title}</div>
                        <div className="text-sm text-black/60">{submission.publisher}</div>
                      </div>
                      <Badge>{submission.status}</Badge>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-black/72">{submission.rationale}</p>
                    <a href={submission.url} className="mt-3 inline-block text-sm text-accent hover:text-ink">
                      Open source
                    </a>
                  </div>
                ))
              ) : (
                <div className="rounded-[1.5rem] border border-dashed border-black/10 p-4 text-sm text-black/60">
                  No source submissions submitted yet for this contributor.
                </div>
              )}
            </div>
          </Panel>
        </div>
      </section>
    </main>
  );
}
