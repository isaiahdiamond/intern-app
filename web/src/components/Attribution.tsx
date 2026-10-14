import type { Listing } from "@/lib/api";

export default function Attribution({
  listings,
  onPhoto,
}: {
  listings: Listing[];
  onPhoto?: boolean;
}) {
  if (!listings.some((listing) => listing.source === "adzuna")) return null;
  return (
    <div
      className="px-1 pt-4 font-mono text-meta"
      style={{
        color: onPhoto ? "var(--color-ink-inverse)" : "var(--color-ink-3)",
      }}
    >
      Jobs by Adzuna
    </div>
  );
}
