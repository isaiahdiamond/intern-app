import type { LucideIcon } from "lucide-react"

export function ActivityChips({
  items,
}: {
  items: { icon: LucideIcon; text: string }[]
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {items.map(({ icon: Icon, text }) => (
        <span
          key={text}
          className="flex items-center gap-1.5 rounded-[8px] border border-line bg-surface px-2.5 py-1 font-mono text-data text-text-2"
        >
          <Icon className="size-3.5 text-text-3" />
          {text}
        </span>
      ))}
    </div>
  )
}
