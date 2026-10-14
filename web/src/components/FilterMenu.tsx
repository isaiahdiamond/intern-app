import { Chevron } from "./Icon";

export type Option = {
  key: string;
  label: string;
  count: number | null;
  on: boolean;
};

export default function FilterMenu({
  label,
  value,
  open,
  active,
  muted,
  options,
  onToggle,
  onPick,
}: {
  label: string;
  value: string;
  open: boolean;
  active: boolean;
  muted?: boolean;
  options: Option[];
  onToggle: () => void;
  onPick: (key: string) => void;
}) {
  return (
    <div className="relative" style={{ opacity: muted ? 0.45 : 1 }}>
      <button
        type="button"
        disabled={muted}
        onClick={(event) => {
          event.stopPropagation();
          onToggle();
        }}
        className={[
          "box-border flex h-10 cursor-pointer items-center gap-2 rounded-full border px-4 text-control whitespace-nowrap transition-colors select-none",
          active
            ? "border-transparent bg-ink text-ink-inverse"
            : "border-line-strong bg-surface text-ink hover:bg-hover",
          muted ? "cursor-not-allowed" : "",
        ].join(" ")}
      >
        <span>{label}</span>
        {value ? (
          <span className={active ? "font-normal" : "font-normal text-ink-3"}>
            {value}
          </span>
        ) : null}
        <span className="opacity-60">
          <Chevron flip={open} />
        </span>
      </button>

      {open ? (
        <div
          onClick={(event) => event.stopPropagation()}
          className="absolute top-12 left-0 z-40 max-h-80 w-65 animate-pop overflow-auto overscroll-contain rounded-lg border border-line-strong bg-surface p-1 shadow-float"
        >
          {options.map((option) => (
            <div
              key={option.key}
              onClick={() => onPick(option.key)}
              className="flex h-10 cursor-pointer items-center gap-3 rounded-md px-3 text-control text-ink hover:bg-hover"
            >
              <span
                className="box-border flex size-4 shrink-0 items-center justify-center rounded-xs border text-ink-inverse"
                style={{
                  background: option.on ? "var(--color-ink)" : "#fff",
                  borderColor: option.on
                    ? "var(--color-ink)"
                    : "var(--color-line-strong)",
                }}
              >
                <svg
                  width="11"
                  height="11"
                  viewBox="0 0 12 12"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}
                  aria-hidden="true"
                  style={{ opacity: option.on ? 1 : 0 }}
                >
                  <path
                    d="M2.5 6.2l2.4 2.3 4.6-5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </span>
              <span className="min-w-0 flex-1 truncate">{option.label}</span>
              <span className="font-mono text-tag text-ink-3">
                {option.count === null ? "" : option.count.toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
