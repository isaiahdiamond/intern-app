import type { Listing } from "@/lib/api";

export default function Attribution({ listings }: { listings: Listing[] }) {
  if (!listings.some((listing) => listing.source === "adzuna")) return null;
  return (
    <div
      className="px-1 pt-4 font-mono text-meta"
      style={{ color: "var(--title-ink-2)" }}
    >
      Jobs by Adzuna
    </div>
  );
}
