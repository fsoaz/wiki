import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { SiteHeader } from "@/components/site-header";
import { Panel } from "@/components/ui";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function signIn(formData: FormData) {
  "use server";

  const email = String(formData.get("email") ?? "");
  const nextPath = String(formData.get("next") ?? "/");
  const response = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
    cache: "no-store",
  });

  if (!response.ok) {
    redirect("/signin?error=1");
  }

  const payload = (await response.json()) as { token: string };
  const cookieStore = await cookies();
  cookieStore.set("wikiai_token", payload.token, { httpOnly: true, sameSite: "lax", path: "/" });
  redirect(nextPath);
}

async function signOut() {
  "use server";
  const cookieStore = await cookies();
  cookieStore.delete("wikiai_token");
  redirect("/");
}

export default async function SignInPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string; error?: string }>;
}) {
  const { next = "/", error } = await searchParams;

  return (
    <main className="min-h-screen pb-16">
      <SiteHeader />
      <section className="mx-auto max-w-4xl px-6 py-10 lg:px-10">
        <div className="mb-8">
          <div className="text-xs uppercase tracking-[0.22em] text-black/55">Demo access</div>
          <h1 className="mt-3 font-serif text-5xl tracking-tight">Sign in as a seeded role</h1>
          <p className="mt-3 max-w-2xl text-base leading-7 text-black/72">
            This MVP uses seeded demo accounts and token-backed sessions to enforce contributor and reviewer access.
          </p>
        </div>
        {error ? <div className="mb-6 text-sm text-ember">Could not sign in with that account.</div> : null}
        <div className="grid gap-6 md:grid-cols-3">
          {[
            ["contributor@example.com", "Contributor", "Create suggestions and source submissions."],
            ["reviewer@example.com", "Reviewer", "Access review queue and approve or reject items."],
            ["admin@example.com", "Admin", "Full reviewer-level access for MVP governance paths."],
          ].map(([email, label, description]) => (
            <Panel key={email} className="p-6">
              <div className="text-xs uppercase tracking-[0.22em] text-black/55">{label}</div>
              <div className="mt-3 text-sm leading-6 text-black/72">{description}</div>
              <form action={signIn} className="mt-6">
                <input type="hidden" name="email" value={email} />
                <input type="hidden" name="next" value={next} />
                <button className="rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white" type="submit">
                  Continue as {label}
                </button>
              </form>
            </Panel>
          ))}
        </div>
        <form action={signOut} className="mt-8">
          <button className="text-sm text-black/60 underline" type="submit">
            Clear local session
          </button>
        </form>
      </section>
    </main>
  );
}
