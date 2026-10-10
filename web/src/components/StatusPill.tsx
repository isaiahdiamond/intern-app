import { Check, ChevronDown } from "lucide-react"

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export const statuses = [
  "new",
  "interested",
  "applied",
  "interviewing",
  "offer",
  "rejected",
] as const

export type Status = (typeof statuses)[number]

export const statusLabel: Record<Status, string> = {
  new: "New",
  interested: "Interested",
  applied: "Applied",
  interviewing: "Interviewing",
  offer: "Offer",
  rejected: "Rejected",
}

const pillClass: Record<Status, string> = {
  new: "text-status-new-text bg-status-new-bg",
  interested: "text-status-interested-text bg-status-interested-bg",
  applied: "text-status-applied-text bg-status-applied-bg",
  interviewing: "text-status-interviewing-text bg-status-interviewing-bg",
  offer: "text-status-offer-text bg-status-offer-bg",
  rejected: "text-status-rejected-text bg-status-rejected-bg",
}

export function StatusPill({
  status,
  onChange,
}: {
  status: Status
  onChange: (next: Status) => void
}) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        onClick={(event) => event.stopPropagation()}
        className={`flex h-[22px] shrink-0 items-center gap-1 rounded-pill px-2 text-data ${pillClass[status]}`}
      >
        {statusLabel[status]}
        <ChevronDown className="size-3 opacity-50" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" onClick={(event) => event.stopPropagation()}>
        {statuses.map((name) => (
          <DropdownMenuItem key={name} onSelect={() => onChange(name)}>
            <Check className={`size-3.5 ${name === status ? "opacity-100" : "opacity-0"}`} />
            {statusLabel[name]}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
