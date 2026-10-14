import { status, statuses, tracked } from "@/lib/api";
import { Check, Chevron } from "./Icon";

export function StatusPill({
  value,
  wide,
  chevron,
  onClick,
}: {
  value: string;
  wide?: boolean;
  chevron?: boolean;
  onClick?: (event: React.MouseEvent) => void;
}) {
  const current = status(value);
  return (
    <div
      onClick={onClick}
      className="box-border flex h-7 items-center gap-2 rounded-full px-3 text-control"
      style={{
        background: current.bg,
        color: current.fg,
        width: wide ? 124 : undefined,
        cursor: onClick ? "pointer" : "default",
      }}
    >
      <span
        className="size-2 shrink-0 rounded-full"
        style={{ background: current.dot }}
      />
      <span className="truncate">{current.label}</span>
      {chevron ? (
        <span className="ml-auto opacity-60">
          <Chevron />
        </span>
      ) : null}
    </div>
  );
}

export function StatusMenu({
  value,
  includeNew,
  onPick,
  style,
}: {
  value: string;
  includeNew?: boolean;
  onPick: (next: string) => void;
  style?: React.CSSProperties;
}) {
  const options = includeNew ? statuses : tracked;
  return (
    <div
      onClick={(event) => event.stopPropagation()}
      className="absolute z-30 w-50 animate-pop overflow-auto overscroll-contain rounded-lg border border-line-strong bg-surface p-1 shadow-float"
      style={style}
    >
      {options.map((option) => (
        <div
          key={option.key}
          onClick={(event) => {
            event.stopPropagation();
            onPick(option.key);
          }}
          className="flex h-10 cursor-pointer items-center gap-3 rounded-md px-3 text-control text-ink hover:bg-hover"
        >
          <span
            className="size-2 shrink-0 rounded-full"
            style={{ background: option.dot }}
          />
          <span>{option.label}</span>
          <Check on={option.key === value} />
        </div>
      ))}
    </div>
  );
}
