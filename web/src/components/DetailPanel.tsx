import { useEffect, useRef, useState } from "react";
import type { Listing } from "@/lib/api";
import { ago, fullDate, status } from "@/lib/api";
import { paths } from "@/lib/icons";
import { External, Icon } from "./Icon";
import { StatusMenu, StatusPill } from "./StatusPill";

const labels: Record<string, string> = {
  undergrad: "Undergraduate",
  masters: "Masters",
  phd: "PhD",
  any: "Any degree",
  intern: "Intern",
  coop: "Co-op",
  new_grad: "New grad",
  other: "Other",
};

const nextStatus: Record<string, string> = {
  new: "saved",
  saved: "applied",
  applied: "interviewing",
  interviewing: "offer",
};

export default function DetailPanel({
  listing,
  position,
  onPrev,
  onNext,
  onClose,
  onStatus,
}: {
  listing: Listing;
  position: string;
  onPrev: () => void;
  onNext: () => void;
  onClose: () => void;
  onStatus: (next: string) => void;
}) {
  const header = useRef<HTMLDivElement>(null);
  const [menu, setMenu] = useState(false);
  const next = nextStatus[listing.status];

  useEffect(() => {
    header.current?.focus();
  }, []);

  const props: {
    label: string;
    icon: string;
    value: string;
    mono?: boolean;
    meta?: string;
  }[] = [
    { label: "Location", icon: paths.pin, value: listing.location },
    {
      label: "Posted",
      icon: paths.cal,
      value: listing.posted_at ? fullDate(listing.posted_at) : "unknown",
      mono: true,
      meta: listing.posted_at ? ago(listing.posted_at) : "",
    },
    {
      label: "Source",
      icon: paths.globe,
      value: listing.source,
      meta: listing.source === "adzuna" ? "Jobs by Adzuna" : "",
    },
    {
      label: "Industry",
      icon: paths.dash,
      value: listing.industry || "unclassified",
    },
    {
      label: "Preference",
      icon: paths.target,
      value:
        listing.industry_rank === 999
          ? "unranked"
          : `#${listing.industry_rank} industry`,
      mono: true,
    },
    {
      label: "Posting",
      icon: paths.profile,
      value: listing.full_text ? "full description stored" : "link only",
    },
  ];
  if (listing.level || listing.education) {
    props.push({
      label: "Level",
      icon: paths.profile,
      value: [listing.level, listing.education]
        .filter(Boolean)
        .map((key) => labels[key] ?? key)
        .join(" · "),
    });
  }
  if (listing.term)
    props.push({ label: "Term", icon: paths.cal, value: listing.term });
  if (listing.copies > 1) {
    props.push({
      label: "Duplicates",
      icon: paths.copies,
      value: `${listing.copies} postings collapsed`,
      mono: true,
    });
  }

  return (
    <div className="flex h-full flex-col" style={{ width: "var(--panel-w)" }}>
      <div
        ref={header}
        tabIndex={-1}
        className="flex h-16 shrink-0 items-center gap-1 border-b border-line-soft pr-4 pl-6 outline-none"
      >
        <span className="font-mono text-meta text-ink-3">{position}</span>
        <div className="ml-auto flex gap-1 text-ink-3">
          <button
            type="button"
            onClick={onPrev}
            aria-label="Previous listing"
            title="Previous listing"
            className="flex size-9 items-center justify-center rounded-full hover:bg-hover"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 12 12"
              fill="none"
              stroke="currentColor"
              strokeWidth={1.5}
              aria-hidden="true"
            >
              <path
                d="M3 7.5l3-3 3 3"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
          <button
            type="button"
            onClick={onNext}
            aria-label="Next listing"
            title="Next listing"
            className="flex size-9 items-center justify-center rounded-full hover:bg-hover"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 12 12"
              fill="none"
              stroke="currentColor"
              strokeWidth={1.5}
              aria-hidden="true"
            >
              <path
                d="M3 4.5l3 3 3-3"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close panel"
            title="Close panel"
            className="flex size-9 items-center justify-center rounded-full hover:bg-hover"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 12 12"
              fill="none"
              stroke="currentColor"
              strokeWidth={1.5}
              aria-hidden="true"
            >
              <path d="M3 3l6 6M9 3l-6 6" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-auto overscroll-contain px-6 pt-6 pb-12">
        <div className="flex size-12 items-center justify-center rounded-md bg-tile text-[22px]">
          🏢
        </div>
        <h2 className="mt-4 mb-0 text-section text-ink text-pretty">
          {listing.display_title}
        </h2>
        <div className="mt-1 text-body text-ink-3">{listing.company}</div>

        <div className="mt-5 flex gap-2">
          <a
            href={listing.url}
            target="_blank"
            rel="noreferrer"
            className="flex h-10 items-center gap-2 rounded-full bg-ink pr-4 pl-[14px] text-control text-ink-inverse no-underline transition-colors hover:bg-black hover:no-underline motion-safe:active:scale-[0.96]"
          >
            Open posting
            <External />
          </a>
          <button
            type="button"
            onClick={() => onStatus(next ?? "hidden")}
            className="flex h-10 items-center rounded-full bg-track px-4 text-control text-ink transition-colors hover:bg-ink/10"
          >
            {next ? `Mark ${status(next).label.toLowerCase()}` : "Archive"}
          </button>
        </div>

        <div className="mt-8 text-label text-ink-3 uppercase">Properties</div>
        <div className="mt-3 flex flex-col">
          {props.map((prop) => (
            <div key={prop.label} className="flex min-h-10 items-center py-1">
              <span className="w-30 shrink-0 text-label text-ink-3 uppercase">
                {prop.label}
              </span>
              <span className="mr-2 shrink-0 text-ink-3">
                <Icon path={prop.icon} />
              </span>
              <span
                className="min-w-0 text-body text-ink-2 break-words"
                style={{
                  fontFamily: prop.mono ? "var(--font-mono)" : undefined,
                }}
              >
                {prop.value}
              </span>
              {prop.meta ? (
                <span className="ml-2 shrink-0 font-mono text-tag whitespace-nowrap text-ink-3">
                  {prop.meta}
                </span>
              ) : null}
            </div>
          ))}

          <div className="relative flex h-10 items-center">
            <span className="w-30 shrink-0 text-label text-ink-3 uppercase">
              Status
            </span>
            <StatusPill
              value={listing.status}
              chevron
              onClick={(event) => {
                event.stopPropagation();
                setMenu(!menu);
              }}
            />
            {menu ? (
              <StatusMenu
                value={listing.status}
                onPick={(key) => {
                  setMenu(false);
                  onStatus(key);
                }}
                style={{ left: 120, top: 36 }}
              />
            ) : null}
          </div>

          <div className="flex h-10 items-center">
            <span className="w-30 shrink-0 text-label text-ink-3 uppercase">
              Link
            </span>
            <span className="mr-2 shrink-0 text-ink-3">
              <Icon path={paths.link} />
            </span>
            <a
              href={listing.url}
              target="_blank"
              rel="noreferrer"
              className="truncate text-body"
              title={listing.url}
            >
              {listing.url}
            </a>
          </div>
        </div>

        <div className="my-6 h-px bg-line-soft" />
        <div className="text-label text-ink-3 uppercase">Raw posting title</div>
        <div className="mt-2 text-body text-ink-2 text-pretty">
          {listing.title}
        </div>

        <div className="mt-5 rounded-md bg-surface-sunk px-4 py-3 text-body text-ink-2">
          Skill extraction has not run on this listing, so there are no parsed
          requirements yet.
        </div>
      </div>
    </div>
  );
}
