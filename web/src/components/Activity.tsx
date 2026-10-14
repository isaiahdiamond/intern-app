import { useState } from "react";
import { Chevron } from "./Icon";

export type Company = { company: string; has_icon: boolean };
export type Entry = { day: string; count: number; companies: Company[] };
export type Activity = { days: number; ranges: number[]; entries: Entry[] };

// Share of the plot's height the tallest bar takes, leaving the rest for the
// avatar stack above it. DESIGN.md keeps the plot's own floor in --plot-h.
const barShare = 36;

function label(day: string) {
  const date = new Date(`${day}T00:00:00`);
  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

// Three of the nine companies applied to have no icon, so the monogram is a
// normal state and not a fallback for a broken image.
function Avatar({ company, has_icon }: Company) {
  const [broken, setBroken] = useState(false);
  if (!has_icon || broken) {
    return (
      <span
        title={company}
        className="flex size-6 shrink-0 items-center justify-center rounded-full border-2 border-surface bg-tile text-[11px] font-semibold text-ink-3"
      >
        {company.slice(0, 1).toUpperCase()}
      </span>
    );
  }
  return (
    <span
      title={company}
      className="flex size-6 shrink-0 items-center justify-center overflow-hidden rounded-full border-2 border-surface bg-surface"
    >
      <img
        src={`/api/icon/${encodeURIComponent(company)}`}
        alt=""
        aria-hidden="true"
        loading="lazy"
        onError={() => setBroken(true)}
        className="size-4 object-contain"
      />
    </span>
  );
}

// Lives in the page header beside the greeting, not in the card, but it is the
// activity chart's control so it stays in the activity chart's file.
export function RangeMenu({
  days,
  ranges,
  onPick,
}: {
  days: number;
  ranges: number[];
  onPick: (days: number) => void;
}) {
  const [open, setOpen] = useState(false);
  return (
    <div className="relative shrink-0">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        aria-haspopup="menu"
        aria-expanded={open}
        className="flex h-10 items-center gap-2 rounded-full border border-line-strong bg-surface px-4 text-control text-ink hover:bg-hover"
      >
        Last {days} days
        <Chevron flip={open} />
      </button>
      {open ? (
        <>
          <div className="fixed inset-0 z-30" onClick={() => setOpen(false)} />
          <div className="absolute top-12 right-0 z-40 w-44 animate-pop rounded-lg border border-line-strong bg-surface p-1 shadow-float">
            {ranges.map((range) => (
              <button
                type="button"
                key={range}
                onClick={() => {
                  onPick(range);
                  setOpen(false);
                }}
                className="flex h-10 w-full items-center rounded-md px-3 text-control text-ink hover:bg-hover"
                style={{
                  background: range === days ? "var(--color-hover)" : undefined,
                }}
              >
                Last {range} days
              </button>
            ))}
          </div>
        </>
      ) : null}
    </div>
  );
}

export default function ActivityChart({
  days,
  data,
}: {
  days: number;
  data: Activity | null;
}) {
  const entries = data ? data.entries : [];
  const peak = Math.max(1, ...entries.map((entry) => entry.count));
  const total = entries.reduce((sum, entry) => sum + entry.count, 0);

  // Wide ranges leave each column a few pixels, so the stack shrinks with it
  // and the dates thin out rather than collide.
  const stack = days <= 14 ? 6 : days <= 30 ? 2 : 1;
  // Past 30 days a column is narrower than the dot, so the baseline would read
  // as a solid rule rather than as one mark per day.
  const dot = days <= 30 ? "var(--dot-day)" : "var(--dot-day-wide)";
  const step = Math.ceil(entries.length / 7);

  return (
    <div className="card flex min-w-0 flex-col rounded-2xl p-6">
      <div className="min-w-0">
        <div className="text-section text-ink">Applications sent</div>
        <div className="mt-1 font-mono text-meta text-ink-3 tabular-nums">
          {total} in the last {days} days
        </div>
      </div>

      <div className="mt-5 flex min-h-[var(--plot-h)] flex-1 items-end gap-[5px] border-b border-line-soft">
        {data ? null : (
          <div className="skeleton h-[var(--bar-share)] w-full self-end rounded-sm" />
        )}
        {entries.map((entry) => {
          const shown = entry.companies.slice(-stack);
          const rest = entry.companies.length - shown.length;
          return (
            <div
              key={entry.day}
              title={`${label(entry.day)} · ${entry.count} sent`}
              className="flex h-full min-w-0 flex-1 flex-col items-center justify-end gap-2"
            >
              {entry.count ? (
                <>
                  <div className="flex flex-col-reverse items-center">
                    {shown.map((company) => (
                      <span
                        key={company.company}
                        className="mt-[var(--avatar-lap)]"
                      >
                        <Avatar {...company} />
                      </span>
                    ))}
                  </div>
                  {rest > 0 ? (
                    <span className="-mt-1 rounded-full bg-tile px-1.5 font-mono text-[11px] text-ink-3 tabular-nums">
                      +{rest}
                    </span>
                  ) : null}
                  <div
                    className="w-full max-w-2.5 rounded-full bg-ink"
                    style={{
                      height: `${Math.max(3, (entry.count / peak) * barShare)}%`,
                      minHeight: 10,
                    }}
                  />
                </>
              ) : (
                <div
                  className="shrink-0 rounded-full bg-chart-dot"
                  style={{ width: dot, height: dot }}
                />
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-3 flex min-h-3 gap-[5px]">
        {entries.map((entry, index) => (
          <div
            key={entry.day}
            className="min-w-0 flex-1 font-mono text-tag whitespace-nowrap text-ink-3"
            style={{
              textAlign: index === entries.length - 1 ? "right" : "left",
            }}
          >
            {index === entries.length - 1
              ? "Today"
              : index % step === 0
                ? label(entry.day)
                : ""}
          </div>
        ))}
      </div>
    </div>
  );
}
