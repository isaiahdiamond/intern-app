import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import type { Listing, Page, Tracked } from "@/lib/api"
import { ago, get, lastDays, monthKey, saveStatus, status } from "@/lib/api"
import Attribution from "@/components/Attribution"
import DetailPanel from "@/components/DetailPanel"
import { Icon } from "@/components/Icon"
import { paths } from "@/lib/icons"
import Layout from "@/components/Layout"
import { CompanyCell, RoleCell } from "@/components/Row"
import { StatusPill } from "@/components/StatusPill"

const pieKeys = ["applied", "interviewing", "offer", "rejected"]

export default function Dashboard() {
  const navigate = useNavigate()
  const [rec, setRec] = useState<Listing[]>([])
  const [recTotal, setRecTotal] = useState(0)
  const [tracker, setTracker] = useState<Tracked[]>([])
  const [counts, setCounts] = useState<Record<string, number>>({})
  const [selected, setSelected] = useState<number | null>(null)

  const [tick, setTick] = useState(0)

  useEffect(() => {
    async function load() {
      const page = await get<Page>("/api/listings?sort=rank&per_page=6")
      if (page) {
        setRec(page.listings)
        setRecTotal(page.total)
      }
      const board = await get<{ listings: Tracked[]; counts: Record<string, number> }>(
        "/api/tracker"
      )
      if (board) {
        setTracker(board.listings)
        setCounts(board.counts)
      }
    }
    load()
  }, [tick])

  const rows = [...rec, ...tracker]
  const current = rows.find((row) => row.id === selected) ?? null
  const panelOpen = current !== null

  async function move(id: number, next: string) {
    await saveStatus(id, next)
    setSelected(null)
    setTick(tick + 1)
  }

  function step(by: number) {
    const index = rows.findIndex((row) => row.id === selected)
    const row = rows[Math.min(Math.max(index + by, 0), rows.length - 1)]
    if (row) setSelected(row.id)
  }

  const sent = pieKeys.reduce((total, key) => total + (counts[key] ?? 0), 0)
  const month = monthKey()

  function thisMonth(keys: string[]) {
    let total = 0
    for (const row of tracker) {
      for (const entry of row.history) {
        if (keys.includes(entry.status) && entry.changed_at.startsWith(month)) total += 1
      }
    }
    return total
  }

  const cards = [
    { label: "Applications", value: sent, icon: paths.send, tint: "rgba(10,132,255,0.10)", ink: "#0066CC", delta: thisMonth(["applied"]), neutral: false },
    { label: "Interviews", value: counts.interviewing ?? 0, icon: paths.cal, tint: "rgba(175,82,222,0.12)", ink: "#7A3DA8", delta: thisMonth(["interviewing"]), neutral: false },
    { label: "Rejections", value: counts.rejected ?? 0, icon: paths.cross, tint: "rgba(0,0,0,0.05)", ink: "#6E6E73", delta: thisMonth(["rejected"]), neutral: true },
    { label: "Offers", value: counts.offer ?? 0, icon: paths.offer, tint: "rgba(48,176,199,0.15)", ink: "#0B6E80", delta: thisMonth(["offer"]), neutral: false },
  ]

  const days = lastDays(28)
  for (const row of tracker) {
    for (const entry of row.history) {
      if (entry.status !== "applied") continue
      const day = days.find((item) => item.key === entry.changed_at.slice(0, 10))
      if (day) day.count += 1
    }
  }
  const peak = Math.max(2, ...days.map((day) => day.count))

  let sweep = 0
  const stops = pieKeys.map((key) => {
    const from = sweep
    sweep += ((counts[key] ?? 0) / (sent || 1)) * 360
    return `${status(key).dot} ${from}deg ${sweep}deg`
  })

  const recCols = panelOpen
    ? "minmax(0,1fr) minmax(0,1.3fr) minmax(0,0.9fr) 52px"
    : "minmax(140px,1fr) minmax(0,1.8fr) minmax(0,1fr) 60px"
  const appCols = panelOpen
    ? "minmax(0,1fr) minmax(0,1.4fr) 56px 108px"
    : "minmax(140px,1fr) minmax(0,2.2fr) 72px 108px"

  return (
    <Layout
      title="Dashboard"
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
      <div className="mb-5 grid gap-4 [grid-template-columns:repeat(auto-fit,minmax(max(136px,calc(25%-12px)),1fr))]">
        {cards.map((card) => (
          <div
            key={card.label}
            className="relative min-w-0 overflow-hidden rounded-card border border-line-soft bg-surface px-5 pt-5 pb-[18px] shadow-card"
          >
            <div className="flex min-w-0 flex-col">
              <span className="pr-11 text-[13px] leading-5 font-medium text-text-3">
                {card.label}
              </span>
              <span className="mt-3.5 font-display text-[34px] leading-none font-semibold tracking-[-0.035em] tabular-nums">
                {card.value}
              </span>
              <span
                className="mt-3.5 box-border flex h-[22px] max-w-full items-center self-start truncate rounded-sm px-2 text-[11.5px] font-medium"
                style={{
                  background:
                    card.neutral || card.delta === 0
                      ? "rgba(0,0,0,0.045)"
                      : "rgba(52,199,89,0.12)",
                  color: card.neutral ? "#6E6E73" : card.delta > 0 ? "#1E7A34" : "#86868B",
                }}
              >
                {card.delta > 0 ? "↑ " : ""}
                {card.delta} this month
              </span>
            </div>
            <div
              className="absolute top-4 right-4 flex size-9 items-center justify-center rounded-menu"
              style={{ background: card.tint, color: card.ink }}
            >
              <Icon path={card.icon} size={17} stroke={1.5} />
            </div>
          </div>
        ))}
      </div>

      <div className="mb-5 grid gap-5 [grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr))]">
        <div className="min-w-0 overflow-hidden rounded-card border border-line-soft bg-surface shadow-card">
          <div className="flex h-[58px] items-center gap-2.5 px-5">
            <span className="font-display text-[15px] font-semibold tracking-[-0.012em] whitespace-nowrap">
              Applications sent
            </span>
            <span className="flex h-5 shrink-0 items-center rounded-[10px] bg-black/5 px-[7px] font-mono text-[11px] font-medium text-text-2">
              {sent} total
            </span>
            <span className="ml-auto truncate font-mono text-[11px] text-text-4">
              per day · 28 days
            </span>
          </div>
          <div className="px-5 pt-1.5 pb-[18px]">
            <div className="flex h-[170px] items-end gap-[5px] border-b border-line-soft [background:repeating-linear-gradient(to_top,transparent_0,transparent_41px,rgba(0,0,0,0.045)_41px,rgba(0,0,0,0.045)_42px)]">
              {days.map((day) => (
                <div
                  key={day.key}
                  title={`${day.date.toLocaleDateString("en-US", { month: "short", day: "numeric" })} · ${day.count} sent`}
                  className="flex h-full min-w-0 flex-1 flex-col items-center justify-end gap-1"
                >
                  <span className="font-mono text-[10.5px] leading-none text-text-2">
                    {day.count ? day.count : ""}
                  </span>
                  <div
                    className="w-full max-w-4 rounded-t-[5px] rounded-b-[2px]"
                    style={{
                      height: day.count ? Math.round((day.count / peak) * 118) : 3,
                      background: day.count ? "rgba(10,132,255,0.55)" : "#EDEDF0",
                    }}
                  />
                </div>
              ))}
            </div>
            <div className="mt-2.5 flex gap-[5px]">
              {days.map((day, index) => (
                <div
                  key={day.key}
                  className="min-w-0 flex-1 font-mono text-[10.5px] whitespace-nowrap text-text-4"
                  style={{ textAlign: index === 27 ? "right" : "left" }}
                >
                  {index === 27
                    ? "Today"
                    : index % 7 === 0
                      ? day.date.toLocaleDateString("en-US", { month: "short", day: "numeric" })
                      : ""}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="min-w-0 overflow-hidden rounded-card border border-line-soft bg-surface shadow-card">
          <div className="flex h-[58px] items-center px-5">
            <span className="font-display text-[15px] font-semibold tracking-[-0.012em] whitespace-nowrap">
              Applications by status
            </span>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-x-[26px] gap-y-[22px] px-6 pt-2 pb-6">
            <div
              className="relative size-[156px] shrink-0 rounded-full"
              style={{ background: sent ? `conic-gradient(${stops.join(",")})` : "#EDEDF0" }}
            >
              <div className="absolute inset-5 flex flex-col items-center justify-center gap-[3px] rounded-full bg-surface shadow-[inset_0_0_0_1px_rgba(0,0,0,0.04)]">
                <span className="font-display text-[30px] leading-none font-semibold tracking-[-0.035em]">
                  {sent}
                </span>
                <span className="text-[11.5px] text-text-4">Applications</span>
              </div>
            </div>
            <div className="flex min-w-40 flex-1 flex-col gap-1">
              {pieKeys.map((key) => (
                <div
                  key={key}
                  className="flex h-[34px] items-center gap-2.5 rounded-control bg-head px-2.5 text-[13px]"
                >
                  <span
                    className="size-2.5 shrink-0 rounded-[3px]"
                    style={{ background: status(key).dot }}
                  />
                  <span className="whitespace-nowrap">
                    {key === "applied" ? "Awaiting reply" : status(key).label}
                  </span>
                  <span className="ml-auto font-mono text-[12px] font-medium">
                    {Math.round(((counts[key] ?? 0) / (sent || 1)) * 100)}%
                  </span>
                  <span className="w-6 text-right font-mono text-[11.5px] text-text-4">
                    ({counts[key] ?? 0})
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-5">
        <div className="min-w-0 overflow-hidden rounded-card border border-line-soft bg-surface shadow-card">
          <div className="flex h-[58px] items-center gap-2.5 px-5">
            <span className="font-display text-[15px] font-semibold tracking-[-0.012em] whitespace-nowrap">
              Top of your board
            </span>
            <span className="flex h-5 shrink-0 items-center rounded-[10px] bg-black/5 px-[7px] font-mono text-[11px] font-medium text-text-2">
              {recTotal.toLocaleString()} new
            </span>
            <button
              type="button"
              onClick={() => navigate("/listings")}
              className="ml-auto flex h-7 items-center gap-1 rounded-control px-2.5 text-[12.5px] font-medium text-accent-text hover:bg-accent/[0.08]"
            >
              View all
              <svg width="10" height="10" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth={1.7}>
                <path d="M4.5 2.5L8 6l-3.5 3.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </div>
          <div
            className="grid h-[34px] items-center gap-4 border-y border-line-row bg-head pr-5 pl-[34px] text-[11px] font-semibold tracking-[0.04em] text-text-5 uppercase"
            style={{ gridTemplateColumns: recCols }}
          >
            <span>Company</span>
            <span>Role</span>
            <span>Industry</span>
            <span className="text-right">Posted</span>
          </div>
          {rec.map((listing, index) => (
            <div
              key={listing.id}
              onClick={() => setSelected(listing.id)}
              className="relative grid h-[62px] items-center gap-4 pr-5 pl-[34px] transition-colors duration-100 hover:bg-[#FAFAFC]"
              style={{
                gridTemplateColumns: recCols,
                borderTop: index === 0 ? "none" : "1px solid rgba(0,0,0,0.05)",
                background: selected === listing.id ? "rgba(10,132,255,0.07)" : "transparent",
              }}
            >
              <span className="absolute top-1/2 left-[15px] -mt-[3px] size-1.5 rounded-full bg-accent" />
              <CompanyCell listing={listing} size={34} />
              <RoleCell listing={listing} bold />
              <span className="truncate text-[12.5px] text-text-3">
                {listing.industry || "unclassified"}
              </span>
              <span className="text-right font-mono text-[11.5px] whitespace-nowrap text-text-3">
                {ago(listing.posted_at)}
              </span>
            </div>
          ))}
        </div>

        <div className="min-w-0 overflow-hidden rounded-card border border-line-soft bg-surface shadow-card">
          <div className="flex h-[58px] items-center gap-2.5 px-5">
            <span className="font-display text-[15px] font-semibold tracking-[-0.012em] whitespace-nowrap">
              Your applications
            </span>
            <span className="flex h-5 shrink-0 items-center rounded-[10px] bg-black/5 px-[7px] font-mono text-[11px] font-medium text-text-2">
              {tracker.length}
            </span>
            <button
              type="button"
              onClick={() => navigate("/tracker")}
              className="ml-auto flex h-7 items-center gap-1 rounded-control px-2.5 text-[12.5px] font-medium text-accent-text hover:bg-accent/[0.08]"
            >
              View all
              <svg width="10" height="10" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth={1.7}>
                <path d="M4.5 2.5L8 6l-3.5 3.5" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </div>
          <div
            className="grid h-[34px] items-center gap-4 border-y border-line-row bg-head px-5 text-[11px] font-semibold tracking-[0.04em] text-text-5 uppercase"
            style={{ gridTemplateColumns: appCols }}
          >
            <span>Company</span>
            <span>Role</span>
            <span>Changed</span>
            <span className="text-right">Status</span>
          </div>
          {tracker.length === 0 ? (
            <div className="px-4 py-10 text-center text-text-3">
              Nothing tracked yet. Add a listing from{" "}
              <button
                type="button"
                onClick={() => navigate("/listings")}
                className="text-accent-text underline"
              >
                All listings
              </button>{" "}
              and it shows up here.
            </div>
          ) : (
            tracker.slice(0, 6).map((listing, index) => (
              <div
                key={listing.id}
                onClick={() => setSelected(listing.id)}
                className="relative grid h-[62px] items-center gap-4 px-5 transition-colors duration-100 hover:bg-[#FAFAFC]"
                style={{
                  gridTemplateColumns: appCols,
                  borderTop: index === 0 ? "none" : "1px solid rgba(0,0,0,0.05)",
                  background: selected === listing.id ? "rgba(10,132,255,0.07)" : "transparent",
                }}
              >
                <CompanyCell listing={listing} size={34} />
                <RoleCell listing={listing} bold={false} />
                <span className="font-mono text-[11.5px] whitespace-nowrap text-text-3">
                  {listing.status_changed_at ? ago(listing.status_changed_at) : "—"}
                </span>
                <div className="flex justify-end">
                  <StatusPill value={listing.status} wide />
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <Attribution listings={rows} />
    </Layout>
  )
}
