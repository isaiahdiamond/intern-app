import type { Status } from "@/components/StatusPill"

export type Listing = {
  id: number
  title: string
  company: string
  domain?: string
  location: string
  posted: string
  source: string
  status: Status
  skills: string[]
  url: string
}

export function shortDate(iso: string) {
  if (!iso) return ""
  const days = Math.round((Date.now() - new Date(iso).getTime()) / 86400000)
  if (days <= 0) return "today"
  if (days < 30) return `${days}d`
  if (days < 365) return `${Math.round(days / 30)}mo`
  return `${Math.round(days / 365)}y`
}

export function longDate(iso: string) {
  if (!iso) return "unknown"
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}
