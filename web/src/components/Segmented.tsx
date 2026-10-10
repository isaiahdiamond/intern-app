export function Segmented({
  options,
  value,
  onChange,
}: {
  options: { value: string; label: string; count: number }[]
  value: string
  onChange: (next: string) => void
}) {
  return (
    <div className="inline-flex gap-0.5 rounded-[8px] bg-hover p-0.5">
      {options.map((option) => {
        const active = option.value === value
        return (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            aria-pressed={active}
            className={`flex items-center gap-1.5 rounded-[6px] px-3 py-1 text-label transition-colors duration-150 ease-smooth ${
              active
                ? "bg-surface text-text shadow-[0_1px_2px_rgba(0,0,0,0.06)]"
                : "text-text-2 hover:text-text"
            }`}
          >
            {option.label}
            <span className="font-mono text-data text-text-3">{option.count}</span>
          </button>
        )
      })}
    </div>
  )
}
