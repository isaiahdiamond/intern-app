import { useState } from "react";
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
  const [menu, setMenu] = useState(false);
  const next = nextStatus[listing.status];

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
    <div className="flex h-full w-panel flex-col">
      <div className="flex h-[52px] shrink-0 items-center gap-1.5 border-b border-line-soft pr-3.5 pl-6">
        <span className="font-mono text-[11.5px] text-text-4">{position}</span>
        <div className="ml-auto flex gap-0.5 text-text-3">
          <button
            type="button"
            onClick={onPrev}
            aria-label="Previous listing"
            className="flex size-7 items-center justify-center rounded-[7px] hover:bg-black/5"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 12 12"
              fill="none"
              stroke="currentColor"
              strokeWidth={1.5}
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
            className="flex size-7 items-center justify-center rounded-[7px] hover:bg-black/5"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 12 12"
              fill="none"
              stroke="currentColor"
              strokeWidth={1.5}
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
            className="flex size-7 items-center justify-center rounded-[7px] hover:bg-black/5"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 12 12"
              fill="none"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path d="M3 3l6 6M9 3l-6 6" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-auto overscroll-contain px-6 pt-6 pb-8">
        <div className="flex size-10 items-center justify-center rounded-menu bg-tile text-[20px]">
          🏢
        </div>
        <h2 className="mt-3.5 mb-0 text-[20px] leading-[1.25] font-semibold tracking-[-0.018em] text-pretty">
          {listing.display_title}
        </h2>
        <div className="mt-1 text-[13px] text-text-3">{listing.company}</div>

        <div className="mt-[18px] flex gap-2">
          <a
            href={listing.url}
            target="_blank"
            rel="noreferrer"
            className="flex h-[30px] items-center gap-1.5 rounded-control bg-accent px-3.5 text-[13px] font-medium text-white no-underline hover:bg-accent-hover hover:no-underline"
          >
            Open posting
            <External size={11} />
          </a>
          <button
            type="button"
            onClick={() => onStatus(next ?? "hidden")}
            className="flex h-[30px] items-center rounded-control bg-track px-3.5 text-[13px] font-medium hover:bg-[rgba(118,118,128,0.18)]"
          >
            {next ? `Mark ${status(next).label.toLowerCase()}` : "Archive"}
          </button>
        </div>

        <div className="mt-[26px] text-[11.5px] font-semibold text-text-4">
          Properties
        </div>
        <div className="mt-2 flex flex-col">
          {props.map((prop) => (
            <div key={prop.label} className="flex min-h-8 items-center py-1">
              <span className="w-[104px] shrink-0 text-[12.5px] text-text-4">
                {prop.label}
              </span>
              <span className="mr-2 shrink-0 text-text-4">
                <Icon path={prop.icon} size={14} />
              </span>
              <span
                className="min-w-0 text-[13px] break-words"
                style={{
                  fontFamily: prop.mono ? "var(--font-mono)" : undefined,
                }}
              >
                {prop.value}
              </span>
              {prop.meta ? (
                <span className="ml-2 shrink-0 font-mono text-[11px] whitespace-nowrap text-text-4">
                  {prop.meta}
                </span>
              ) : null}
            </div>
          ))}

          <div className="relative flex h-8 items-center">
            <span className="w-[104px] shrink-0 text-[12.5px] text-text-4">
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
                style={{ left: 104, top: 30 }}
              />
            ) : null}
          </div>

          <div className="flex h-8 items-center">
            <span className="w-[104px] shrink-0 text-[12.5px] text-text-4">
              Link
            </span>
            <span className="mr-2 shrink-0 text-text-4">
              <Icon path={paths.link} size={14} />
            </span>
            <a
              href={listing.url}
              target="_blank"
              rel="noreferrer"
              className="truncate text-[13px]"
              title={listing.url}
            >
              {listing.url}
            </a>
          </div>
        </div>

        <div className="my-5 mb-[18px] h-px bg-line-soft" />
        <div className="text-[11.5px] font-semibold text-text-4">
          Raw posting title
        </div>
        <div className="mt-2 text-[13px] text-pretty">{listing.title}</div>

        <div className="mt-[18px] flex items-center gap-2.5 rounded-menu bg-bg px-3.5 py-3 text-[12.5px] text-text-2">
          Skill extraction has not run on this listing, so there are no parsed
          requirements yet.
        </div>
      </div>
    </div>
  );
}
