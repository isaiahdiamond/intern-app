import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Filters, Listing, Page, Tracked } from "@/lib/api";
import { ago, get, lastDays, monthKey, saveStatus, status } from "@/lib/api";
import Attribution from "@/components/Attribution";
import DetailPanel from "@/components/DetailPanel";
import Layout from "@/components/Layout";
import { ColumnHead, CompanyCell, RoleCell } from "@/components/Row";
import { StatusPill } from "@/components/StatusPill";

const pieKeys = ["applied", "interviewing", "offer", "rejected"];

export default function Dashboard() {
  const navigate = useNavigate();
  const [rec, setRec] = useState<Listing[]>([]);
  const [recTotal, setRecTotal] = useState(0);
  const [board, setBoard] = useState(0);
  const [tracker, setTracker] = useState<Tracked[]>([]);
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [roles, setRoles] = useState<{ name: string; count: number | null }[]>(
    [],
  );
  const [selected, setSelected] = useState<number | null>(null);
  const [loaded, setLoaded] = useState(false);

  const [tick, setTick] = useState(0);

  useEffect(() => {
    async function load() {
      const page = await get<Page>(
        "/api/listings?match_profile=true&sort=newest&per_page=6",
      );
      if (page) {
        setRec(page.listings);
        setRecTotal(page.total);
      }
      const all = await get<Page>("/api/listings?per_page=1");
      if (all) setBoard(all.total);
      const tracked = await get<{
        listings: Tracked[];
        counts: Record<string, number>;
      }>("/api/tracker");
      if (tracked) {
        setTracker(tracked.listings);
        setCounts(tracked.counts);
      }
      setLoaded(true);
    }
    load();
  }, [tick]);

  useEffect(() => {
    async function load() {
      const filters = await get<Filters>("/api/filters");
      if (!filters) return;
      setRoles(filters.roles.map((name) => ({ name, count: null })));
      const counted = await Promise.all(
        filters.roles.map(async (name) => {
          const page = await get<Page>(
            `/api/listings?per_page=1&role=${encodeURIComponent(name)}`,
          );
          return { name, count: page ? page.total : null };
        }),
      );
      setRoles(counted);
    }
    load();
  }, []);

  const rows = [...rec, ...tracker];
  const current = rows.find((row) => row.id === selected) ?? null;
  const panelOpen = current !== null;

  async function move(id: number, next: string) {
    await saveStatus(id, next);
    setSelected(null);
    setTick(tick + 1);
  }

  function step(by: number) {
    const index = rows.findIndex((row) => row.id === selected);
    const row = rows[Math.min(Math.max(index + by, 0), rows.length - 1)];
    if (row) setSelected(row.id);
  }

  const sent = pieKeys.reduce((total, key) => total + (counts[key] ?? 0), 0);
  const month = monthKey();

  function thisMonth(key: string) {
    let total = 0;
    for (const row of tracker) {
      for (const entry of row.history) {
        if (entry.status === key && entry.changed_at.startsWith(month))
          total += 1;
      }
    }
    return total;
  }

  const cards = [
    {
      label: "Applications",
      value: sent,
      caption: `of ${tracker.length} tracked`,
      delta: thisMonth("applied"),
    },
    {
      label: "Interviews",
      value: counts.interviewing ?? 0,
      caption: `of ${sent} sent`,
      delta: thisMonth("interviewing"),
    },
    {
      label: "Rejections",
      value: counts.rejected ?? 0,
      caption: `of ${sent} sent`,
      delta: thisMonth("rejected"),
    },
    {
      label: "Offers",
      value: counts.offer ?? 0,
      caption: `of ${sent} sent`,
      delta: thisMonth("offer"),
    },
  ];

  const days = lastDays(28);
  for (const row of tracker) {
    for (const entry of row.history) {
      if (entry.status !== "applied") continue;
      const day = days.find(
        (item) => item.key === entry.changed_at.slice(0, 10),
      );
      if (day) day.count += 1;
    }
  }
  const peak = Math.max(2, ...days.map((day) => day.count));

  let sweep = 0;
  const stops = pieKeys.map((key) => {
    const from = sweep;
    sweep += ((counts[key] ?? 0) / (sent || 1)) * 360;
    return `${status(key).dot} ${from}deg ${sweep}deg`;
  });

  const recCols = panelOpen
    ? "minmax(140px,1fr) minmax(0,1.6fr) 92px"
    : "minmax(180px,1.1fr) minmax(0,2fr) 100px";
  const appCols = panelOpen
    ? "minmax(160px,1fr) minmax(0,1.6fr) 0 124px"
    : "minmax(220px,1.1fr) minmax(0,2.4fr) 120px 124px";

  return (
    <Layout
      title="Dashboard"
      slot="dashboard"
      panel={
        current ? (
          <DetailPanel
            listing={current}
            position={`${status(current.status).label.toLowerCase()} · ${rows.findIndex((row) => row.id === current.id) + 1} of ${rows.length}`}
            onPrev={() => step(-1)}
            onNext={() => step(1)}
            onClose={() => setSelected(null)}
            onStatus={(next) => move(current.id, next)}
          />
        ) : null
      }
    >
      <div className="mb-6 grid gap-4 [grid-template-columns:repeat(4,minmax(0,1fr))_320px]">
        {cards.map((card) => (
          <div
            key={card.label}
            className="card flex min-h-34 min-w-0 flex-col rounded-xl p-5"
          >
            <span className="truncate text-label text-ink-3 uppercase">
              {card.label}
            </span>
            <div className="mt-4 flex items-end gap-2">
              <span className="text-display text-ink tabular-nums">
                {card.value}
              </span>
              <span
                className="mb-1 ml-auto flex h-6 shrink-0 items-center rounded-sm px-2 font-mono text-tag tabular-nums"
                style={{
                  background:
                    card.delta > 0
                      ? "rgba(52,199,89,0.14)"
                      : "rgba(23,23,23,0.05)",
                  color: card.delta > 0 ? "#1E7A34" : "var(--color-ink-3)",
                }}
              >
                {card.delta > 0 ? "↑" : "→"} {card.delta}
              </span>
            </div>
            <span className="mt-2 truncate text-meta text-ink-3">
              {card.caption}
            </span>
          </div>
        ))}

        <button
          type="button"
          onClick={() => navigate("/listings")}
          aria-label={`${recTotal.toLocaleString()} listings match your profile. Open all listings.`}
          className="hero-card image-outline relative flex min-h-[200px] flex-col justify-end overflow-hidden rounded-xl p-5 text-left shadow-card"
          style={{
            background:
              "linear-gradient(145deg, #2E2E2E 0%, #171717 55%, #000000 100%)",
          }}
        >
          <img
            src="/img/hero-card-dashboard.jpg"
            alt=""
            aria-hidden="true"
            loading="eager"
            decoding="async"
            className="absolute inset-0 size-full object-cover object-bottom"
          />
          <div className="relative z-1 flex flex-col">
            <span className="text-display text-ink-inverse tabular-nums">
              {recTotal.toLocaleString()}
            </span>
            <span className="mt-1 text-lead font-medium text-white/80">
              match your profile
            </span>
          </div>
        </button>
      </div>

      <div className="mb-6 grid gap-6 [grid-template-columns:minmax(0,1fr)_340px]">
        <div className="flex min-w-0 flex-col gap-6">
          <div className="card min-w-0 rounded-2xl p-6">
            <div className="flex items-center gap-3">
              <span className="text-section text-ink">Applications sent</span>
              <span className="ml-auto font-mono text-meta text-ink-3">
                per day · 28 days
              </span>
            </div>
            <div className="mt-5 flex h-[170px] items-end gap-[5px] border-b border-line-soft">
              {days.map((day) => (
                <div
                  key={day.key}
                  title={`${day.date.toLocaleDateString("en-US", { month: "short", day: "numeric" })} · ${day.count} sent`}
                  className="flex h-full min-w-0 flex-1 flex-col items-center justify-end gap-1"
                >
                  <span className="font-mono text-tag text-ink-2 tabular-nums">
                    {day.count ? day.count : ""}
                  </span>
                  <div
                    className="w-full max-w-4 rounded-t-sm"
                    style={{
                      height: day.count
                        ? Math.round((day.count / peak) * 118)
                        : 3,
                      background: day.count
                        ? "var(--color-ink)"
                        : "var(--color-tile)",
                    }}
                  />
                </div>
              ))}
            </div>
            <div className="mt-3 flex gap-[5px]">
              {days.map((day, index) => (
                <div
                  key={day.key}
                  className="min-w-0 flex-1 font-mono text-tag whitespace-nowrap text-ink-3"
                  style={{ textAlign: index === 27 ? "right" : "left" }}
                >
                  {index === 27
                    ? "Today"
                    : index % 7 === 0
                      ? day.date.toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                        })
                      : ""}
                </div>
              ))}
            </div>
          </div>

          <div className="card min-w-0 rounded-2xl p-3">
            <div className="flex items-center gap-3 px-3 py-3">
              <span className="text-section text-ink">Top of your board</span>
              <button
                type="button"
                onClick={() => navigate("/listings")}
                className="ml-auto h-9 rounded-full px-3 text-control text-ink-3 hover:bg-hover"
              >
                View all
              </button>
            </div>
            <ColumnHead
              columns={recCols}
              labels={["Company", "Role", "Posted"]}
            />
            {rec.map((listing) => (
              <div
                key={listing.id}
                onClick={() => setSelected(listing.id)}
                className="relative grid cursor-pointer items-center gap-4 border-t border-line-soft pr-4 pl-6 transition-colors duration-[var(--duration-hover)] hover:bg-row-hover"
                style={{
                  gridTemplateColumns: recCols,
                  height: "var(--row-h)",
                  background:
                    selected === listing.id
                      ? "var(--color-selected)"
                      : undefined,
                }}
              >
                {selected === listing.id ? (
                  <span className="absolute top-1/2 left-0 h-10 w-[2px] -translate-y-1/2 bg-ink" />
                ) : null}
                {listing.status === "new" ? (
                  <span className="absolute top-1/2 left-2 size-1.5 -translate-y-1/2 rounded-full bg-accent" />
                ) : null}
                <CompanyCell listing={listing} />
                <RoleCell listing={listing} bold />
                <span className="truncate font-mono text-meta text-ink-3">
                  {ago(listing.posted_at)}
                </span>
              </div>
            ))}
            {loaded && rec.length === 0 ? (
              <div className="animate-in px-4 py-12 text-center text-lead text-ink-2">
                No listings match your profile yet.
              </div>
            ) : null}
          </div>
        </div>

        <div className="flex min-w-0 flex-col gap-6">
          <div className="card rounded-xl p-5">
            <div className="flex items-center gap-3">
              <span className="text-section text-ink">Target roles</span>
              <button
                type="button"
                onClick={() => navigate("/onboarding")}
                className="ml-auto h-9 rounded-full border border-line-strong bg-surface px-4 text-control text-ink hover:bg-hover"
              >
                Edit
              </button>
            </div>
            <div className="mt-3 flex flex-col">
              {roles.map((role) => (
                <div
                  key={role.name}
                  className="flex h-10 items-center gap-3 border-t border-line-soft text-body text-ink-2 first:border-t-0"
                >
                  <span className="truncate">{role.name}</span>
                  <span className="ml-auto font-mono text-meta text-ink-3 tabular-nums">
                    {role.count === null ? "" : role.count.toLocaleString()}
                  </span>
                </div>
              ))}
              <div className="mt-3 border-t border-line-soft pt-3 font-mono text-meta text-ink-3 tabular-nums">
                {board.toLocaleString()} listings on the board
              </div>
            </div>
          </div>

          <div className="card rounded-xl p-5">
            <span className="text-section text-ink">
              Applications by status
            </span>
            <div className="mt-5 flex justify-center">
              <div
                className="relative size-[156px] shrink-0 rounded-full"
                style={{
                  background: sent
                    ? `conic-gradient(${stops.join(",")})`
                    : "var(--color-tile)",
                }}
              >
                <div className="absolute inset-5 flex flex-col items-center justify-center gap-1 rounded-full bg-surface">
                  <span className="text-display text-ink tabular-nums">
                    {sent}
                  </span>
                  <span className="text-meta text-ink-3">sent</span>
                </div>
              </div>
            </div>
            <div className="mt-5 flex flex-col gap-1">
              {pieKeys.map((key) => (
                <div
                  key={key}
                  className="flex h-10 items-center gap-3 rounded-md bg-surface-sunk px-3 text-body text-ink-2"
                >
                  <span
                    className="size-2.5 shrink-0 rounded-xs"
                    style={{ background: status(key).dot }}
                  />
                  <span className="truncate">
                    {key === "applied" ? "Awaiting reply" : status(key).label}
                  </span>
                  <span className="ml-auto font-mono text-meta text-ink tabular-nums">
                    {Math.round(((counts[key] ?? 0) / (sent || 1)) * 100)}%
                  </span>
                  <span className="w-6 text-right font-mono text-tag text-ink-3 tabular-nums">
                    {counts[key] ?? 0}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="card min-w-0 rounded-2xl p-3">
        <div className="flex items-center gap-3 px-3 py-3">
          <span className="text-section text-ink">Your applications</span>
          <span className="font-mono text-meta text-ink-3 tabular-nums">
            {tracker.length}
          </span>
          <button
            type="button"
            onClick={() => navigate("/tracker")}
            className="ml-auto h-9 rounded-full px-3 text-control text-ink-3 hover:bg-hover"
          >
            View all
          </button>
        </div>
        <ColumnHead
          columns={appCols}
          labels={["Company", "Role", "Changed", "Status"]}
        />
        {!loaded ? null : tracker.length === 0 ? (
          <div className="animate-in px-4 py-12 text-center text-lead text-ink-2">
            Nothing tracked yet. Save a listing from{" "}
            <button
              type="button"
              onClick={() => navigate("/listings")}
              className="underline"
            >
              All listings
            </button>{" "}
            and it shows up here.
          </div>
        ) : (
          tracker.slice(0, 6).map((listing) => (
            <div
              key={listing.id}
              onClick={() => setSelected(listing.id)}
              className="relative grid cursor-pointer items-center gap-4 border-t border-line-soft pr-4 pl-6 transition-colors duration-[var(--duration-hover)] hover:bg-row-hover"
              style={{
                gridTemplateColumns: appCols,
                height: "var(--row-h)",
                background:
                  selected === listing.id ? "var(--color-selected)" : undefined,
              }}
            >
              {selected === listing.id ? (
                <span className="absolute top-1/2 left-0 h-10 w-[2px] -translate-y-1/2 bg-ink" />
              ) : null}
              <CompanyCell listing={listing} />
              <RoleCell listing={listing} bold={false} />
              <span className="truncate font-mono text-meta text-ink-3">
                {panelOpen
                  ? ""
                  : listing.status_changed_at
                    ? ago(listing.status_changed_at)
                    : "—"}
              </span>
              <div className="flex justify-start">
                <StatusPill value={listing.status} wide />
              </div>
            </div>
          ))
        )}
      </div>

      <Attribution listings={rows} onPhoto />
    </Layout>
  );
}
