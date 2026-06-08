import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { SiteHeader } from "@/components/site-header";
import { Badge, Panel } from "@/components/ui";
import { getAdminOverview, getAdminSessions, getAuthSession, revokeAdminSession } from "@/lib/api";

export default async function AdminPage() {
  const user = await getAuthSession();
  if (!user) {
    redirect("/signin?next=/admin");
  }

  const overview = await getAdminOverview();
  if (!overview) {
    redirect("/review");
  }
  const sessions = await getAdminSessions();

  async function revokeSessionAction(formData: FormData) {
    "use server";

    const sessionId = String(formData.get("session_id") ?? "");
    const ok = await revokeAdminSession(sessionId);
    if (!ok) {
      redirect("/admin");
    }
    revalidatePath("/admin");
    redirect("/admin");
  }

  return (
    <main className="min-h-screen pb-16">
      <SiteHeader />
      <section className="mx-auto max-w-7xl px-6 py-8 lg:px-10">
        <div className="mb-8 space-y-3">
          <div className="text-xs uppercase tracking-[0.22em] text-black/55">Admin dashboard</div>
          <h1 className="font-serif text-5xl tracking-tight">Audit and system activity</h1>
          <p className="max-w-3xl text-base leading-7 text-black/72">
            Protected admin surface for workflow visibility and recent accountability events.
          </p>
        </div>
        <div className="mb-6 flex flex-wrap gap-3 text-sm text-black/70">
          <Badge>{user.role}</Badge>
          <Badge>{overview.audit_event_count} audit events</Badge>
          <Badge>{overview.review_queue_count} queue items</Badge>
          <Badge>{overview.active_session_count} active sessions</Badge>
        </div>
        <Panel className="p-6">
          <div className="text-xs uppercase tracking-[0.22em] text-black/55">Recent audit events</div>
          <div className="mt-4 space-y-3">
            {overview.recent_audit_entries.map((entry) => (
              <div key={entry.id} className="rounded-[1.5rem] border border-black/10 bg-white/75 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <div className="font-medium">{entry.action}</div>
                    <div className="text-sm text-black/60">
                      {entry.actor_email ?? "system"} · {entry.subject_type}
                    </div>
                  </div>
                  <Badge>{entry.actor_role ?? "system"}</Badge>
                </div>
                {entry.details_json ? (
                  <pre className="mt-3 overflow-x-auto rounded-2xl bg-mist/80 p-3 text-xs leading-6 text-black/70">
                    {entry.details_json}
                  </pre>
                ) : null}
              </div>
            ))}
          </div>
        </Panel>
        <Panel className="mt-6 p-6">
          <div className="text-xs uppercase tracking-[0.22em] text-black/55">Active sessions</div>
          <div className="mt-4 space-y-3">
            {sessions?.map((session) => (
              <div key={session.id} className="rounded-[1.5rem] border border-black/10 bg-white/75 p-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <div className="font-medium">{session.user_email}</div>
                    <div className="text-sm text-black/60">{session.user_role}</div>
                  </div>
                  <form action={revokeSessionAction}>
                    <input type="hidden" name="session_id" value={session.id} />
                    <button className="rounded-full border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-ink" type="submit">
                      Revoke
                    </button>
                  </form>
                </div>
              </div>
            )) ?? null}
          </div>
        </Panel>
      </section>
    </main>
  );
}
