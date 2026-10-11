import { status, statuses, tracked } from "@/lib/api"
import { Check, Chevron } from "./Icon"

export function StatusPill({
  value,
  wide,
  chevron,
  onClick,
}: {
  value: string
  wide?: boolean
  chevron?: boolean
  onClick?: (event: React.MouseEvent) => void
}) {
  const current = status(value)
  return (
    <div
      onClick={onClick}
      className="box-border flex h-[22px] items-center gap-1.5 rounded-[11px] px-2.5 text-[12px] font-medium"
      style={{
        background: current.bg,
        color: current.fg,
        width: wide ? 108 : undefined,
        cursor: onClick ? "pointer" : "default",
      }}
    >
      <span className="size-1.5 shrink-0 rounded-full" style={{ background: current.dot }} />
      <span className="truncate">{current.label}</span>
      {chevron ? (
        <span className="ml-auto opacity-60">
          <Chevron />
        </span>
      ) : null}
    </div>
  )
}

export function StatusMenu({
  value,
  includeNew,
  onPick,
  style,
}: {
  value: string
  includeNew?: boolean
  onPick: (next: string) => void
  style?: React.CSSProperties
}) {
  const options = includeNew ? statuses : tracked
  return (
    <div
      onClick={(event) => event.stopPropagation()}
      className="absolute z-30 w-44 animate-pop rounded-menu border border-line-strong bg-surface p-[5px] shadow-menu"
      style={style}
    >
      {options.map((option) => (
        <div
          key={option.key}
          onClick={(event) => {
            event.stopPropagation()
            onPick(option.key)
          }}
          className="flex h-7 items-center gap-2.5 rounded-sm px-2.5 text-[12.5px] hover:bg-accent/10"
        >
          <span className="size-[7px] rounded-full" style={{ background: option.dot }} />
          <span>{option.label}</span>
          <Check on={option.key === value} />
        </div>
      ))}
    </div>
  )
}
