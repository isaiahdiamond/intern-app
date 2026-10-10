import { useEffect } from "react"
import { ExternalLink, X } from "lucide-react"

import { FavIcon } from "@/components/FavIcon"
import { StatusPill, type Status } from "@/components/StatusPill"
import { Button } from "@/components/ui/button"
import type { Listing } from "@/lib/listings"
import { longDate } from "@/lib/listings"

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex gap-4 py-1.5">
      <span className="w-24 shrink-0 text-label text-text-3">{label}</span>
      <span className="min-w-0 flex-1 text-body">{value}</span>
    </div>
  )
}

export function DetailPanel({
  listing,
  onClose,
  onStatus,
}: {
  listing: Listing
  onClose: () => void
  onStatus: (next: Status) => void
}) {
  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") onClose()
    }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [onClose])

  return (
    <aside
      aria-label="Listing detail"
      className="fixed inset-y-0 right-0 z-20 flex w-panel max-w-full flex-col border-l border-line bg-surface shadow-panel motion-safe:animate-[slide-in_180ms_cubic-bezier(0.2,0.8,0.2,1)]"
    >
      <div className="flex items-start gap-3 border-b border-line p-5">
        <FavIcon domain={listing.domain} />
        <div className="min-w-0 flex-1">
          <h2 className="text-section">{listing.title}</h2>
          <p className="text-label text-text-2">{listing.company}</p>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close">
          <X className="size-4" />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-5">
        <Row label="Location" value={listing.location} />
        <Row label="Posted" value={longDate(listing.posted)} />
        <Row label="Source" value={listing.source} />
        <div className="flex gap-4 py-1.5">
          <span className="w-24 shrink-0 text-label text-text-3">Status</span>
          <StatusPill status={listing.status} onChange={onStatus} />
        </div>

        <h3 className="mt-6 mb-2 text-label text-text-3">Requirements</h3>
        {listing.skills.length > 0 ? (
          <div className="flex flex-wrap gap-1.5">
            {listing.skills.map((skill) => (
              <span key={skill} className="rounded-pill bg-hover px-2 py-0.5 font-mono text-data text-text-2">
                {skill}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-body text-text-2">
            This listing came from a list that carries no description, so there is nothing to
            read here. Open the posting to see the requirements.
          </p>
        )}
      </div>

      <div className="border-t border-line p-5">
        <Button asChild className="w-full">
          <a href={listing.url} target="_blank" rel="noopener noreferrer">
            Open posting
            <ExternalLink className="size-3.5" />
          </a>
        </Button>
      </div>
    </aside>
  )
}
