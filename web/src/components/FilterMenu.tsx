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
      <div
        onClick={(event) => {
          event.stopPropagation();
          if (!muted) onToggle();
        }}
        className="box-border flex h-[30px] items-center gap-1.5 rounded-control border pr-2.5 pl-[11px] text-[12.5px] font-medium whitespace-nowrap transition-colors select-none"
        style={{
          background: active ? "rgba(10,132,255,0.08)" : "#fff",
          borderColor: active ? "rgba(10,132,255,0.35)" : "rgba(0,0,0,0.1)",
          color: active ? "#0066CC" : "#1D1D1F",
        }}
      >
        <span>{label}</span>
        <span
          className="font-normal"
          style={{ color: active ? "#0066CC" : "#86868B" }}
        >
          {value}
        </span>
        <span className="opacity-60">
          <Chevron flip={open} />
        </span>
      </div>

      {open ? (
        <div
          onClick={(event) => event.stopPropagation()}
          className="absolute top-9 left-0 z-40 max-h-80 w-[232px] animate-pop overflow-auto overscroll-contain rounded-menu border border-line-strong bg-surface p-[5px] shadow-menu"
        >
          {options.map((option) => (
            <div
              key={option.key}
              onClick={() => onPick(option.key)}
              className="flex h-[30px] items-center gap-2.5 rounded-sm px-2.5 text-[12.5px] hover:bg-accent/[0.08]"
            >
              <span
                className="box-border flex size-3.5 shrink-0 items-center justify-center rounded-[4px] border text-white"
                style={{
                  background: option.on ? "#0A84FF" : "#fff",
                  borderColor: option.on ? "#0A84FF" : "rgba(0,0,0,0.2)",
                }}
              >
                <svg
                  width="10"
                  height="10"
                  viewBox="0 0 12 12"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}
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
              <span className="font-mono text-[11px] text-text-4">
                {option.count === null ? "" : option.count.toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
