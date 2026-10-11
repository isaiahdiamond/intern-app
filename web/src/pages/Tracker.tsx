import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import type { Tracked } from "@/lib/api"
import { ago, get, saveStatus, status, tracked as trackedStatuses } from "@/lib/api"
import Attribution from "@/components/Attribution"
import DetailPanel from "@/components/DetailPanel"
import { Chevron, Magnifier } from "@/components/Icon"
import Layout from "@/components/Layout"
import { ColumnHead, CompanyCell, RoleCell } from "@/components/Row"
import { StatusMenu, StatusPill } from "@/components/StatusPill"

export default function Tracker() {
  const navigate = useNavigate()
  const [rows, setRows] = useState<Tracked[]>([])
  const [counts, setCounts] = useState<Record<string, number>>({})
  const [filter, setFilter] = useState("all")
  const [query, setQuery] = useState("")
  const [collapsed, setCollapsed] = useState<string[]>([])
  const [menu, setMenu] = useState<string | null>(null)
  const [selected, setSelected] = useState<number | null>(null)

  const [tick, setTick] = useState(0)

  useEffect(() => {
    async function load() {
      const board = await get<{ listings: Tracked[]; counts: Record<string, number> }>(
        "/api/tracker"
      )
      if (!board) return
      setRows(board.listings)
      setCounts(board.counts)
    }
    load()
  }, [tick])

  async function move(id: number, next: string) {
    setMenu(null)
    await saveStatus(id, next)
    setTick(tick + 1)
  }

  const text = query.trim().toLowerCase()
  const matching = rows.filter(
    (row) =>
      !text ||
      [row.display_title, row.title, row.company, row.location].join(" ").toLowerCase().includes(text)
  )

  const groups = trackedStatuses
    .filter((item) => filter === "all" || item.key === filter)
    .map((item) => ({
      ...item,
      rows: matching.filter((row) => row.status === item.key),
    }))
    .filter((group) => group.rows.length > 0 || filter === group.key)

  const visible = groups
    .filter((group) => !collapsed.includes(group.key))
    .flatMap((group) => group.rows)
  const current = visible.find((row) => row.id === selected) ?? null
  const panelOpen = current !== null

  function step(by: number) {
    const index = visible.findIndex((row) => row.id === selected)
    const row = visible[Math.min(Math.max(index + by, 0), visible.length - 1)]
    if (row) setSelected(row.id)
  }

  const columns = panelOpen
    ? "minmax(0,1fr) minmax(0,1.4fr) 56px 108px"
    : "minmax(140px,1fr) minmax(0,2.2fr) 72px 108px"

  const segments = [
    { key: "all", label: "All", count: rows.length },
    ...trackedStatuses.map((item) => ({
      key: item.key,
      label: item.label,
      count: counts[item.key] ?? 0,
    })),
  ]

  return (
    <Layout
      title="Tracker"
      tight
      toolbar={
        <div className="relative flex flex-wrap items-center gap-x-3 gap-y-2.5 px-8 pt-[22px] pb-3.5">
          <div className="flex min-w-0 gap-0.5 overflow-hidden rounded-[9px] bg-track p-0.5">
            {segments.map((segment) => {
              const on = filter === segment.key
              return (
                <button
                  type="button"
                  key={segment.key}
                  onClick={() => setFilter(segment.key)}
                  className="flex h-[26px] items-center gap-1.5 rounded-[7px] px-2.5 text-[12.5px] font-medium whitespace-nowrap transition-all duration-150"
                  style={{
                    background: on ? "#fff" : "transparent",
                    boxShadow: on ? "var(--shadow-seg)" : "none",
                    color: on ? "#1D1D1F" : "#3A3A3C",
                  }}
                >
                  <span>{segment.label}</span>
                  <span className="font-mono text-[11px] text-text-4">{segment.count}</span>
                </button>
              )
            })}
          </div>
          <div className="ml-auto box-border flex h-[30px] max-w-[280px] min-w-[180px] flex-[1_1_180px] items-center gap-[7px] rounded-control border border-line bg-surface px-2.5">
            <Magnifier />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search roles, companies"
              className="min-w-0 flex-1 border-0 bg-transparent text-[12.5px] outline-none"
            />
          </div>
        </div>
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
      {rows.length === 0 ? (
        <div className="rounded-panel border border-line bg-surface px-8 py-16 text-center">
          <div className="text-[17px] font-semibold tracking-[-0.012em]">Nothing tracked yet</div>
          <p className="mx-auto mt-2.5 max-w-[420px] text-[13px] leading-[1.5] text-text-3 text-pretty">
            The tracker holds the listings you are doing something about. Save one from the board and
            it appears here, with its status history.
          </p>
          <button
            type="button"
            onClick={() => navigate("/listings")}
            className="mt-5 inline-flex h-[30px] items-center rounded-control bg-accent px-3.5 text-[13px] font-medium text-white hover:bg-accent-hover"
          >
            Browse all listings
          </button>
        </div>
      ) : (
        <div onClick={() => setMenu(null)} className="rounded-panel border border-line bg-surface">
          <ColumnHead columns={columns} labels={["Company", "Role", "Posted", "Status"]} />
          {groups.map((group, groupIndex) => (
            <div key={group.key}>
              <div
                onClick={() =>
                  setCollapsed(
                    collapsed.includes(group.key)
                      ? collapsed.filter((key) => key !== group.key)
                      : [...collapsed, group.key]
                  )
                }
                className="flex h-[34px] items-center gap-2 border-b border-line-soft bg-head-2 pr-4 pl-3 text-text-4"
                style={{ borderTop: groupIndex === 0 ? "none" : "1px solid rgba(0,0,0,0.06)" }}
              >
                <Chevron size={12} flip={!collapsed.includes(group.key)} />
                <span className="size-2 rounded-full" style={{ background: group.dot }} />
                <span className="text-[12.5px] font-semibold text-text">{group.label}</span>
                <span className="font-mono text-[11.5px]">{group.rows.length}</span>
              </div>
              {collapsed.includes(group.key)
                ? null
                : group.rows.map((listing, index) => (
                    <div
                      key={listing.id}
                      onClick={() => setSelected(listing.id)}
                      className="relative grid h-12 items-center gap-4 pr-4 pl-[30px] transition-colors duration-100 hover:bg-row-hover"
                      style={{
                        gridTemplateColumns: columns,
                        borderTop: index === 0 ? "none" : "1px solid rgba(0,0,0,0.05)",
                        background:
                          selected === listing.id ? "rgba(10,132,255,0.07)" : "transparent",
                      }}
                    >
                      <CompanyCell listing={listing} />
                      <RoleCell listing={listing} bold={false} />
                      <span className="font-mono text-[11.5px] whitespace-nowrap text-text-3">
                        {ago(listing.posted_at)}
                      </span>
                      <div className="flex justify-end">
                        <StatusPill
                          value={listing.status}
                          wide
                          chevron
                          onClick={(event) => {
                            event.stopPropagation()
                            setMenu(menu === `row${listing.id}` ? null : `row${listing.id}`)
                          }}
                        />
                      </div>
                      {menu === `row${listing.id}` ? (
                        <StatusMenu
                          value={listing.status}
                          onPick={(next) => move(listing.id, next)}
                          style={{ right: 16, top: 40 }}
                        />
                      ) : null}
                    </div>
                  ))}
            </div>
          ))}
          {matching.length === 0 ? (
            <div className="px-4 py-10 text-center text-text-3">
              No tracked listings match “{query}”.
            </div>
          ) : null}
        </div>
      )}
      <Attribution listings={rows} />
    </Layout>
  )
}
