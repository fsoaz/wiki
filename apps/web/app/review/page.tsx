import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { SiteHeader } from "@/components/site-header";
import { Badge, Panel } from "@/components/ui";
import { assignReviewItem, getAuthSession, getReviewerOverview, submitReviewDecision } from "@/lib/api";

export default async function ReviewPage({
  searchParams
}: {
  searchParams: Promise<{ status?: string; subject_type?: string }>;
}) {
  const user = await getAuthSession();
  if (!user) {
    redirect("/signin?next=/review");
  }

  const { status, subject_type } = await searchParams;
  const overview = await getReviewerOverview(status, subject_type);

  async function approveAction(formData: FormData) {
    "use server";

    const queueItemId = String(formData.get("queue_item_id") ?? "");
    const notes = String(formData.get("notes") ?? "");
    const ok = await submitReviewDecision(queueItemId, {
      decision: "approved",
      notes: notes || "Approved from reviewer dashboard.",
    });
    if (!ok) {
      redirect("/signin?next=/review");
    }
    revalidatePath("/review");
    redirect("/review");
  }

  async function rejectAction(formData: FormData) {
    "use server";

    const queueItemId = String(formData.get("queue_item_id") ?? "");
    const notes = String(formData.get("notes") ?? "");
    const ok = await submitReviewDecision(queueItemId, {
      decision: "rejected",
      notes: notes || "Rejected from reviewer dashboard.",
    });
    if (!ok) {
      redirect("/signin?next=/review");
    }
    revalidatePath("/review");
    redirect("/review");
  }

  async function assignAction(formData: FormData) {
    "use server";

    const queueItemId = String(formData.get("queue_item_id") ?? "");
    const assigned = await assignReviewItem(queueItemId);
    if (!assigned) {
      redirect("/signin?next=/review");
    }
    revalidatePath("/review");
    redirect("/review");
  }

  return (
    <main className="min-h-screen pb-16">
      <SiteHeader />
      <section className="mx-auto max-w-7xl px-6 py-8 lg:px-10">
        <div className="mb-8 space-y-3">
          <div className="text-xs uppercase tracking-[0.22em] text-black/55">Reviewer dashboard</div>
          <h1 className="font-serif text-5xl tracking-tight">Review queue</h1>
          <p className="max-w-3xl text-base leading-7 text-black/72">
            Authenticated reviewer view for article suggestions and source submissions awaiting moderation.
          </p>
        </div>
        <div className="mb-6 flex flex-wrap gap-3 text-sm text-black/70">
          <Badge>{user.role}</Badge>
          <Badge>{overview?.pending_count ?? 0} pending</Badge>
          <Badge>{overview?.approved_count ?? 0} approved</Badge>
          <Badge>{overview?.rejected_count ?? 0} rejected</Badge>
        </div>
        <Panel className="mb-6 p-5">
          <div className="text-xs uppercase tracking-[0.22em] text-black/55">Filters</div>
          <div className="mt-4 flex flex-wrap gap-3 text-sm">
            <a href="/review" className="rounded-full border border-black/10 px-4 py-2 hover:bg-white">All</a>
            <a href="/review?status=pending" className="rounded-full border border-black/10 px-4 py-2 hover:bg-white">Pending</a>
            <a href="/review?status=approved" className="rounded-full border border-black/10 px-4 py-2 hover:bg-white">Approved</a>
            <a href="/review?status=rejected" className="rounded-full border border-black/10 px-4 py-2 hover:bg-white">Rejected</a>
            <a href="/review?subject_type=suggestion" className="rounded-full border border-black/10 px-4 py-2 hover:bg-white">Suggestions</a>
            <a href="/review?subject_type=source_submission" className="rounded-full border border-black/10 px-4 py-2 hover:bg-white">Sources</a>
          </div>
        </Panel>
        <Panel className="p-6">
          <div className="text-xs uppercase tracking-[0.22em] text-black/55">Queue items</div>
          <div className="mt-4 space-y-3">
            {overview?.items.length ? (
              overview.items.map((item) => (
                <div key={item.id} className="rounded-[1.5rem] border border-black/10 bg-white/75 p-4">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <div className="font-medium">{item.article_title}</div>
                      <div className="text-sm text-black/60">
                        {item.subject_type} · {item.contributor_name}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Badge>{item.status}</Badge>
                      <Badge>{item.priority}</Badge>
                    </div>
                  </div>
                  <div className="mt-2 text-xs uppercase tracking-[0.16em] text-black/50">
                    Assigned {item.assigned_reviewer_email ?? "unassigned"}
                  </div>
                  <p className="mt-3 text-sm leading-6 text-black/72">{item.summary}</p>
                  {item.status === "pending" ? (
                    <div className="mt-4 space-y-3">
                      <form action={assignAction}>
                        <input type="hidden" name="queue_item_id" value={item.id} />
                        <button className="rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink" type="submit">
                          Assign to me
                        </button>
                      </form>
                      <form action={approveAction} className="space-y-3">
                        <input type="hidden" name="queue_item_id" value={item.id} />
                        <textarea
                          name="notes"
                          placeholder="Optional approval notes"
                          className="min-h-20 w-full rounded-2xl border border-black/10 bg-white/80 px-4 py-3 text-sm outline-none"
                        />
                        <button className="rounded-full bg-ink px-4 py-2 text-sm font-semibold text-white" type="submit">
                          Approve
                        </button>
                      </form>
                      <form action={rejectAction} className="space-y-3">
                        <input type="hidden" name="queue_item_id" value={item.id} />
                        <textarea
                          name="notes"
                          placeholder="Optional rejection notes"
                          className="min-h-20 w-full rounded-2xl border border-black/10 bg-white/80 px-4 py-3 text-sm outline-none"
                        />
                        <button className="rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink" type="submit">
                          Reject
                        </button>
                      </form>
                    </div>
                  ) : null}
                  {item.decisions.length ? (
                    <div className="mt-5 border-t border-black/10 pt-4">
                      <div className="text-xs uppercase tracking-[0.16em] text-black/50">Decision history</div>
                      <div className="mt-3 space-y-3">
                        {item.decisions.map((decision) => (
                          <div key={decision.id} className="rounded-2xl bg-mist/80 p-3">
                            <div className="flex flex-wrap items-center justify-between gap-3 text-sm">
                              <span className="font-medium">{decision.decision}</span>
                              <span className="text-black/55">{decision.reviewer_email}</span>
                            </div>
                            {decision.notes ? (
                              <p className="mt-2 text-sm leading-6 text-black/70">{decision.notes}</p>
                            ) : null}
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </div>
              ))
            ) : (
              <div className="rounded-[1.5rem] border border-dashed border-black/10 p-4 text-sm text-black/60">
                No review items match the current filter.
              </div>
            )}
          </div>
        </Panel>
      </section>
    </main>
  );
}
