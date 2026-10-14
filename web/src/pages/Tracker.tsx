import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import type { Tracked } from "@/lib/api";
import {
  ago,
  get,
  saveStatus,
  status,
  tracked as trackedStatuses,
} from "@/lib/api";
import AddJob from "@/components/AddJob";
import Attribution from "@/components/Attribution";
import DetailPanel from "@/components/DetailPanel";
import { Chevron, Icon, Magnifier } from "@/components/Icon";
import { paths } from "@/lib/icons";
import Layout from "@/components/Layout";
import { ColumnHead, CompanyCell, RoleCell } from "@/components/Row";
import { StatusMenu, StatusPill } from "@/components/StatusPill";

export default function Tracker() {
  const navigate = useNavigate();
  const location = useLocation();
  const [rows, setRows] = useState<Tracked[]>([]);
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");
  const [collapsed, setCollapsed] = useState<string[]>([]);
  const [menu, setMenu] = useState<string | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [adding, setAdding] = useState(
    Boolean((location.state as { add?: boolean } | null)?.add),
  );

  const [tick, setTick] = useState(0);

  useEffect(() => {
    async function load() {
      const board = await get<{
        listings: Tracked[];
        counts: Record<string, number>;
      }>("/api/tracker");
      setLoaded(true);
      if (!board) return;
      setRows(board.listings);
      setCounts(board.counts);
    }
    load();
  }, [tick]);

  async function move(id: number, next: string) {
    setMenu(null);
    await saveStatus(id, next);
    setTick(tick + 1);
  }

  const text = query.trim().toLowerCase();
  const matching = rows.filter(
    (row) =>
      !text ||
      [row.display_title, row.title, row.company, row.location]
        .join(" ")
        .toLowerCase()
        .includes(text),
  );

  const groups = trackedStatuses
    .filter((item) => filter === "all" || item.key === filter)
    .map((item) => ({
      ...item,
      rows: matching.filter((row) => row.status === item.key),
    }))
    .filter((group) => group.rows.length > 0 || filter === group.key);

  const visible = groups
    .filter((group) => !collapsed.includes(group.key))
    .flatMap((group) => group.rows);
  const current = visible.find((row) => row.id === selected) ?? null;
  const panelOpen = current !== null;

  function step(by: number) {
    const index = visible.findIndex((row) => row.id === selected);
    const row = visible[Math.min(Math.max(index + by, 0), visible.length - 1)];
    if (row) setSelected(row.id);
  }

  const columns = panelOpen
    ? "minmax(160px,1fr) minmax(0,1.6fr) 0 124px"
    : "minmax(220px,1.1fr) minmax(0,2.4fr) 120px 124px";

  const segments = [
    { key: "all", label: "All", count: rows.length },
    ...trackedStatuses.map((item) => ({
      key: item.key,
      label: item.label,
      count: counts[item.key] ?? 0,
    })),
  ];

  return (
    <Layout
      title="Tracker"
      subtitle="The listings you are doing something about."
      slot="tracker"
      actions={
        <button
          type="button"
          onClick={() => setAdding(true)}
          className="flex h-10 shrink-0 items-center gap-2 rounded-full bg-ink pr-4 pl-[14px] text-control text-ink-inverse transition-colors hover:bg-black motion-safe:active:scale-[0.96]"
        >
          <Icon path={paths.add} />
          Add a job
        </button>
      }
      panel={
        current ? (
          <DetailPanel
            listing={current}
            position={`${status(current.status).label.toLowerCase()} · ${visible.findIndex((row) => row.id === current.id) + 1} of ${visible.length}`}
            onPrev={() => step(-1)}
            onNext={() => step(1)}
            onClose={() => setSelected(null)}
            onStatus={(next) => move(current.id, next)}
          />
        ) : null
      }
    >
      {adding ? (
        <AddJob
          onCancel={() => setAdding(false)}
          onAdded={() => {
            setAdding(false);
            setTick(tick + 1);
          }}
        />
      ) : null}

      <div className="mb-6 flex flex-wrap items-center gap-3">
        <div className="flex min-w-0 gap-1 overflow-hidden rounded-full bg-track p-1">
          {segments.map((segment) => {
            const on = filter === segment.key;
            return (
              <button
                type="button"
                key={segment.key}
                onClick={() => setFilter(segment.key)}
                className="flex h-9 items-center gap-2 rounded-full border px-4 text-control whitespace-nowrap transition-[background-color,box-shadow,color]"
                style={{
                  background: on ? "var(--color-surface)" : "transparent",
                  borderColor: on ? "rgba(23,23,23,0.06)" : "transparent",
                  boxShadow: on ? "var(--shadow-seg)" : "none",
                  color: on ? "var(--color-ink)" : "var(--color-ink-2)",
                }}
              >
                <span>{segment.label}</span>
                <span className="font-mono text-tag text-ink-3">
                  {segment.count}
                </span>
              </button>
            );
          })}
        </div>
        <div className="ml-auto box-border flex h-10 max-w-[300px] min-w-[200px] flex-[1_1_200px] items-center gap-2 rounded-full border border-line-strong bg-surface px-4">
          <Magnifier />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search roles, companies"
            aria-label="Search roles, companies"
            className="min-w-0 flex-1 border-0 bg-transparent text-control text-ink outline-none"
          />
        </div>
      </div>

      {!loaded ? null : rows.length === 0 ? (
        <div className="card animate-in rounded-2xl px-8 py-12 text-center">
          <div className="text-section text-ink">Nothing tracked yet</div>
          <p className="mx-auto mt-3 max-w-[460px] text-lead text-ink-2 text-pretty">
            The tracker holds the listings you are doing something about. Save
            one from the board and it appears here, with its status history — or
            add a job you found somewhere else.
          </p>
          <button
            type="button"
            onClick={() => navigate("/listings")}
            className="mt-6 inline-flex h-10 items-center rounded-full bg-ink px-4 text-control text-ink-inverse transition-colors hover:bg-black motion-safe:active:scale-[0.96]"
          >
            Browse all listings
          </button>
        </div>
      ) : (
        <div onClick={() => setMenu(null)} className="card rounded-2xl p-3">
          <ColumnHead
            columns={columns}
            labels={["Company", "Role", "Posted", "Status"]}
          />
          {groups.map((group) => (
            <div key={group.key}>
              <div
                onClick={() =>
                  setCollapsed(
                    collapsed.includes(group.key)
                      ? collapsed.filter((key) => key !== group.key)
                      : [...collapsed, group.key],
                  )
                }
                className="sticky top-0 z-10 flex h-12 cursor-pointer items-center gap-3 rounded-lg bg-surface-sunk px-6 text-ink-3"
              >
                <Chevron size={14} flip={!collapsed.includes(group.key)} />
                <span
                  className="size-2 rounded-full"
                  style={{ background: group.dot }}
                />
                <span className="text-label text-ink uppercase">
                  {group.label}
                </span>
                <span className="font-mono text-tag">{group.rows.length}</span>
              </div>
              {collapsed.includes(group.key)
                ? null
                : group.rows.map((listing) => (
                    <div
                      key={listing.id}
                      onClick={() => setSelected(listing.id)}
                      className="relative grid cursor-pointer items-center gap-4 border-t border-line-soft pr-4 pl-6 transition-colors duration-[var(--duration-hover)] hover:bg-row-hover"
                      style={{
                        gridTemplateColumns: columns,
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
                      <CompanyCell listing={listing} />
                      <RoleCell listing={listing} bold={false} />
                      <span className="truncate font-mono text-meta text-ink-3">
                        {panelOpen ? "" : ago(listing.posted_at)}
                      </span>
                      <div className="flex justify-start">
                        <StatusPill
                          value={listing.status}
                          wide
                          chevron
                          onClick={(event) => {
                            event.stopPropagation();
                            setMenu(
                              menu === `row${listing.id}`
                                ? null
                                : `row${listing.id}`,
                            );
                          }}
                        />
                      </div>
                      {menu === `row${listing.id}` ? (
                        <StatusMenu
                          value={listing.status}
                          onPick={(next) => move(listing.id, next)}
                          style={{ right: 16, top: 48 }}
                        />
                      ) : null}
                    </div>
                  ))}
            </div>
          ))}
          {matching.length === 0 ? (
            <div className="animate-in px-4 py-12 text-center text-lead text-ink-2">
              No tracked listings match “{query}”.
            </div>
          ) : null}
        </div>
      )}
      <Attribution listings={rows} />
    </Layout>
  );
}
