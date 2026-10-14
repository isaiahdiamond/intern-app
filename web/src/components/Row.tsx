import { useState } from "react";
import type { Listing } from "@/lib/api";
import { titleTags } from "@/lib/api";

// The icon is served from our own origin, not from a logo service, so drawing
// the board tells nobody which companies are on it. A company we have no icon
// for 404s, and the tile below shows through.
export function CompanyCell({
  listing,
  size = 36,
}: {
  listing: Listing;
  size?: number;
}) {
  const [broken, setBroken] = useState(false);
  return (
    <div className="flex min-w-0 items-center gap-3">
      <div
        className="flex shrink-0 items-center justify-center overflow-hidden bg-tile text-[16px]"
        style={{
          width: size,
          height: size,
          borderRadius: size > 36 ? "var(--radius-md)" : "var(--radius-sm)",
        }}
      >
        {broken || !listing.has_icon ? (
          "🏢"
        ) : (
          <img
            src={`/api/icon/${encodeURIComponent(listing.company)}`}
            alt=""
            aria-hidden="true"
            loading="lazy"
            onError={() => setBroken(true)}
            style={{
              width: size - 10,
              height: size - 10,
              objectFit: "contain",
            }}
          />
        )}
      </div>
      <div className="flex min-w-0 flex-col gap-0.5">
        <span className="truncate text-row text-ink">{listing.company}</span>
        <span className="truncate text-meta text-ink-3">
          {listing.location}
        </span>
      </div>
    </div>
  );
}

export function Tag({ label }: { label: string }) {
  return (
    <span className="flex h-[22px] shrink-0 items-center rounded-xs border border-line-soft bg-ink/4 px-2 font-mono text-tag whitespace-nowrap text-ink-2">
      {label}
    </span>
  );
}

export function RoleCell({
  listing,
  bold,
}: {
  listing: Listing;
  bold: boolean;
}) {
  return (
    <div className="flex min-w-0 items-center gap-2 overflow-hidden">
      <span
        className="min-w-0 truncate text-row text-ink"
        style={{ fontWeight: bold ? 600 : 500 }}
        title={listing.title}
      >
        {listing.display_title}
      </span>
      <div className="flex min-w-0 shrink-[9999] items-center gap-2 overflow-hidden">
        {titleTags(listing).map((label) => (
          <Tag key={label} label={label} />
        ))}
      </div>
    </div>
  );
}

export function ColumnHead({
  columns,
  labels,
}: {
  columns: string;
  labels: string[];
}) {
  return (
    <div
      className="grid h-11 items-center gap-4 rounded-lg bg-surface-sunk px-6 text-label text-ink-3 uppercase"
      style={{ gridTemplateColumns: columns }}
    >
      {labels.map((label) => (
        <span key={label} className="truncate">
          {label}
        </span>
      ))}
    </div>
  );
}

// Rows of the exact final height, so the table card is already the right size
// when the data lands and nothing below it moves. `cells` is how many columns
// the table has, so the placeholder lines up with the header above it.
export function SkeletonRows({
  columns,
  cells,
  count,
}: {
  columns: string;
  cells: number;
  count: number;
}) {
  const rows = [];
  for (let index = 0; index < count; index += 1) rows.push(index);
  return (
    <>
      {rows.map((index) => (
        <div
          key={index}
          aria-hidden="true"
          className="grid items-center gap-4 border-t border-line-soft pr-4 pl-6"
          style={{ gridTemplateColumns: columns, height: "var(--row-h)" }}
        >
          <div className="flex min-w-0 items-center gap-3">
            <div className="skeleton size-9 shrink-0 rounded-sm" />
            <div className="flex min-w-0 flex-1 flex-col gap-1.5">
              <div className="skeleton h-3.5 w-28 rounded-xs" />
              <div className="skeleton h-3 w-20 rounded-xs" />
            </div>
          </div>
          <div className="skeleton h-3.5 w-full max-w-[280px] rounded-xs" />
          <div className="skeleton h-3 w-14 rounded-xs" />
          {cells >= 4 ? (
            <div className="skeleton h-7 w-[108px] rounded-full" />
          ) : null}
          {cells >= 5 ? <span /> : null}
        </div>
      ))}
    </>
  );
}
