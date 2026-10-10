import { useEffect, useState } from "react"
import { Search, Sparkles, Wallet } from "lucide-react"

import { ActivityChips } from "@/components/ActivityChips"
import { DetailPanel } from "@/components/DetailPanel"
import { ListingRow } from "@/components/ListingRow"
import Page from "@/components/Page"
import { Segmented } from "@/components/Segmented"
import { statusLabel, statuses, type Status } from "@/components/StatusPill"
import { Input } from "@/components/ui/input"
import mockListings from "@/data/listings.json"
import type { Listing } from "@/lib/listings"

const activity = [
  { icon: Sparkles, text: "12 new since yesterday" },
  { icon: Search, text: "9 sources checked" },
  { icon: Wallet, text: "$0.81 spent so far" },
]

export default function Dashboard() {
  const [listings, setListings] = useState(mockListings as Listing[])
  const [view, setView] = useState("all")
  const [query, setQuery] = useState("")
  const [openId, setOpenId] = useState<number | null>(null)

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      const typing = event.target instanceof HTMLElement && event.target.closest("input, textarea")
      if (typing) return
      if (event.key === "k" && (event.metaKey || event.ctrlKey)) {
        event.preventDefault()
        document.getElementById("dashboard-search")?.focus()
      }
    }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [])

  function setStatus(id: number, next: Status) {
    setListings(listings.map((item) => (item.id === id ? { ...item, status: next } : item)))
  }

  const text = query.trim().toLowerCase()
  const matching = listings.filter((item) => {
    if (view !== "all" && item.status !== view) return false
    if (!text) return true
    return `${item.title} ${item.company} ${item.location}`.toLowerCase().includes(text)
  })

  const counts = Object.fromEntries(
    statuses.map((name) => [name, listings.filter((item) => item.status === name).length]),
  )
  const options = [
    { value: "all", label: "All", count: listings.length },
    ...statuses
      .filter((name) => counts[name] > 0)
      .map((name) => ({ value: name, label: statusLabel[name], count: counts[name] })),
  ]

  const groups = statuses
    .map((name) => ({ name, rows: matching.filter((item) => item.status === name) }))
    .filter((group) => group.rows.length > 0)

  const open = listings.find((item) => item.id === openId)

  return (
    <Page title="Dashboard">
      <div className="mb-6 flex flex-col gap-4">
        <ActivityChips items={activity} />

        <div className="flex flex-wrap items-center justify-between gap-3">
          <Segmented options={options} value={view} onChange={setView} />
          <div className="relative w-full sm:w-72">
            <Search className="pointer-events-none absolute top-1/2 left-3 size-3.5 -translate-y-1/2 text-text-3" />
            <Input
              id="dashboard-search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search roles or companies"
              className="pr-12 pl-8"
            />
            <span className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 font-mono text-data text-text-3">
              ⌘K
            </span>
          </div>
        </div>
      </div>

      <div className="overflow-hidden rounded-card border border-line bg-surface">
        {groups.map((group) => (
          <section key={group.name}>
            <h2 className="flex items-center gap-2 border-b border-line bg-bg/60 px-4 py-2 text-group text-text-3 uppercase">
              {statusLabel[group.name]}
              <span className="font-mono normal-case">{group.rows.length}</span>
            </h2>
            {group.rows.map((listing) => (
              <ListingRow
                key={listing.id}
                listing={listing}
                selected={listing.id === openId}
                onSelect={() => setOpenId(listing.id)}
                onStatus={(next) => setStatus(listing.id, next)}
              />
            ))}
          </section>
        ))}

        {groups.length === 0 && (
          <p className="px-4 py-10 text-center text-body text-text-2">
            Nothing matches that. Clear the search or pick another view.
          </p>
        )}
      </div>

      {open && (
        <DetailPanel
          listing={open}
          onClose={() => setOpenId(null)}
          onStatus={(next) => setStatus(open.id, next)}
        />
      )}
    </Page>
  )
}
