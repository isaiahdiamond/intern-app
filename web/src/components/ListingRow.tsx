import { FavIcon } from "@/components/FavIcon"
import { StatusPill, type Status } from "@/components/StatusPill"
import type { Listing } from "@/lib/listings"
import { shortDate } from "@/lib/listings"

export function ListingRow({
  listing,
  selected,
  onSelect,
  onStatus,
}: {
  listing: Listing
  selected: boolean
  onSelect: () => void
  onStatus: (next: Status) => void
}) {
  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onSelect}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault()
          onSelect()
        }
      }}
      className={`flex h-row items-center gap-3 border-b border-line px-4 ${
        selected ? "bg-selected" : "hover:bg-hover"
      }`}
    >
      <FavIcon domain={listing.domain} />

      <span className="min-w-0 flex-1">
        <span className="block truncate text-body font-medium" title={listing.title}>
          {listing.title}
        </span>
        <span className="block truncate text-label font-normal text-text-2" title={listing.location}>
          {listing.company} · {listing.location}
        </span>
      </span>

      <span className="hidden shrink-0 items-center gap-1.5 md:flex">
        {listing.skills.length > 0 ? (
          listing.skills.slice(0, 3).map((skill) => (
            <span key={skill} className="rounded-pill bg-hover px-1.5 font-mono text-data text-text-2">
              {skill}
            </span>
          ))
        ) : (
          <span className="rounded-pill px-1.5 font-mono text-data text-text-3">link only</span>
        )}
      </span>

      <span className="hidden w-14 shrink-0 text-right font-mono text-data text-text-3 sm:block">
        {shortDate(listing.posted)}
      </span>

      <StatusPill status={listing.status} onChange={onStatus} />
    </div>
  )
}
