import { twMerge } from "tailwind-merge";
import { clsx } from "clsx";

export function cn(...values: Array<string | false | null | undefined>) {
  return twMerge(clsx(values));
}

export function Badge({
  children,
  className
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border border-black/10 bg-white/70 px-3 py-1 text-xs font-medium uppercase tracking-[0.18em] text-black/70",
        className
      )}
    >
      {children}
    </span>
  );
}

export function Panel({
  children,
  className
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("rounded-[2rem] border border-black/10 bg-white/80 shadow-panel backdrop-blur", className)}>
      {children}
    </div>
  );
}

export function ButtonLink({
  href,
  children,
  variant = "primary"
}: {
  href: string;
  children: React.ReactNode;
  variant?: "primary" | "secondary";
}) {
  return (
    <a
      href={href}
      className={cn(
        "inline-flex items-center rounded-full px-5 py-3 text-sm font-semibold transition-transform duration-200 hover:-translate-y-0.5",
        variant === "primary"
          ? "bg-ink text-white"
          : "border border-black/10 bg-white text-ink"
      )}
    >
      {children}
    </a>
  );
}
