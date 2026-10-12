import { useState } from "react";
import type { Listing } from "@/lib/api";
import { titleTags } from "@/lib/api";

// The icon is served from our own origin, not from a logo service, so drawing
// the board tells nobody which companies are on it. A company we have no icon
// for 404s, and the tile below shows through.
export function CompanyCell({
  listing,
  size = 28,
}: {
  listing: Listing;
  size?: number;
}) {
  const radius = size >= 34 ? 9 : 7;
  const [broken, setBroken] = useState(false);
  return (
    <div className="flex min-w-0 items-center gap-2.5">
      <div
        className="flex shrink-0 items-center justify-center overflow-hidden bg-tile"
        style={{
          width: size,
          height: size,
          borderRadius: radius,
          fontSize: size >= 34 ? 14 : 13,
        }}
      >
        {broken || !listing.has_icon ? (
          "🏢"
        ) : (
          <img
            src={`/api/icon/${encodeURIComponent(listing.company)}`}
            alt=""
            loading="lazy"
            onError={() => setBroken(true)}
            style={{ width: size - 8, height: size - 8, objectFit: "contain" }}
          />
        )}
      </div>
      <div className="flex min-w-0 flex-col gap-px">
        <span
          className="truncate"
          style={{
            fontSize: size >= 34 ? 13.5 : 13,
            fontWeight: size >= 34 ? 600 : 500,
            letterSpacing: size >= 34 ? "-0.01em" : undefined,
          }}
        >
          {listing.company}
        </span>
        <span className="truncate text-[12px] text-text-3">
          {listing.location}
        </span>
      </div>
    </div>
  );
}

export function Tag({ label }: { label: string }) {
  return (
    <span className="flex h-[18px] shrink-0 items-center rounded-[5px] border border-line-soft bg-black/[0.035] px-1.5 font-mono text-[10.5px] whitespace-nowrap text-text-2">
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
    <div className="flex min-w-0 items-center gap-2">
      <span
        className="min-w-0 truncate text-[13px]"
        style={{ fontWeight: bold ? 600 : 500 }}
        title={listing.title}
      >
        {listing.display_title}
      </span>
      {titleTags(listing).map((label) => (
        <Tag key={label} label={label} />
      ))}
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
      className="grid h-[34px] items-center gap-4 border-b border-line-soft bg-head-2 pr-4 pl-[30px] text-[11.5px] font-medium text-text-4"
      style={{ gridTemplateColumns: columns }}
    >
      {labels.map((label, index) => (
        <span
          key={label}
          style={{ textAlign: index === labels.length - 1 ? "right" : "left" }}
        >
          {label}
        </span>
      ))}
    </div>
  );
}
