import type { Listing } from "@/lib/api";

export default function Attribution({ listings }: { listings: Listing[] }) {
  if (!listings.some((listing) => listing.source === "adzuna")) return null;
  return (
    <div className="px-1 pt-3 font-mono text-[11px] text-text-4">
      Jobs by Adzuna
    </div>
  );
}
