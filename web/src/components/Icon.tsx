export function Icon({
  path,
  size = 16,
  stroke = 1.5,
}: {
  path: string;
  size?: number;
  stroke?: number;
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 16 16"
      fill="none"
      stroke="currentColor"
      strokeWidth={stroke}
      className="shrink-0"
      aria-hidden="true"
    >
      <path d={path} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function Chevron({
  size = 14,
  flip = false,
}: {
  size?: number;
  flip?: boolean;
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 12 12"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      className="shrink-0 transition-transform"
      style={{ transform: flip ? "rotate(180deg)" : "none" }}
      aria-hidden="true"
    >
      <path d="M3 4.5l3 3 3-3" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function Check({ on }: { on: boolean }) {
  return (
    <svg
      width={14}
      height={14}
      viewBox="0 0 12 12"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.75}
      className="ml-auto text-ink"
      style={{ opacity: on ? 1 : 0 }}
      aria-hidden="true"
    >
      <path
        d="M2.5 6.2l2.4 2.3 4.6-5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function External({ size = 12 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 12 12"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      className="shrink-0 opacity-70"
      aria-hidden="true"
    >
      <path
        d="M4 2.5h5.5V8M9.5 2.5L3 9"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function Magnifier() {
  return (
    <svg
      width={16}
      height={16}
      viewBox="0 0 16 16"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      className="shrink-0 text-ink-3"
      aria-hidden="true"
    >
      <circle cx="7" cy="7" r="4.5" />
      <path d="M10.5 10.5L14 14" strokeLinecap="round" />
    </svg>
  );
}
