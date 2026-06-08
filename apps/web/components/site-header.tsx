import Link from "next/link";
import { cookies } from "next/headers";
import { Badge } from "@/components/ui";

export async function SiteHeader() {
  const cookieStore = await cookies();
  const isSignedIn = Boolean(cookieStore.get("wikiai_token")?.value);

  return (
    <header className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-10">
      <Link href="/" className="flex items-center gap-3">
        <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-ink text-sm font-semibold text-white">
          WA
        </div>
        <div>
          <div className="font-serif text-2xl">WikiAI</div>
          <div className="text-xs uppercase tracking-[0.22em] text-black/55">Trust-first knowledge</div>
        </div>
      </Link>
      <div className="hidden items-center gap-4 md:flex">
        <Link href="/search?q=quantum%20computing" className="text-sm text-black/70 hover:text-black">
          Search
        </Link>
        <Link href="/articles/quantum-computing" className="text-sm text-black/70 hover:text-black">
          Articles
        </Link>
        <Link href="/contributors" className="text-sm text-black/70 hover:text-black">
          Contributors
        </Link>
        <Link href="/review" className="text-sm text-black/70 hover:text-black">
          Review
        </Link>
        <Link href="/admin" className="text-sm text-black/70 hover:text-black">
          Admin
        </Link>
        <Link href={isSignedIn ? "/contributors" : "/signin"} className="text-sm text-black/70 hover:text-black">
          {isSignedIn ? "Session" : "Sign in"}
        </Link>
        <Badge>mvp</Badge>
      </div>
    </header>
  );
}
