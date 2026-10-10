import { useState } from "react"

export function FavIcon({ domain }: { domain?: string }) {
  const [broken, setBroken] = useState(false)

  if (!domain || broken) {
    return (
      <span className="flex size-6 shrink-0 items-center justify-center rounded-pill border border-line bg-hover text-[14px] leading-none">
        🏢
      </span>
    )
  }

  return (
    <img
      src={`/api/favicons/${domain}`}
      alt=""
      width={24}
      height={24}
      onError={() => setBroken(true)}
      className="size-6 shrink-0 rounded-pill border border-line bg-surface object-contain"
    />
  )
}
