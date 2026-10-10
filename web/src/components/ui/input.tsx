import type { ComponentProps } from "react"
import { cn } from "@/lib/utils"

function Input({ className, ...props }: ComponentProps<"input">) {
  return (
    <input
      className={cn(
        "h-8 w-full rounded-control border border-line bg-surface px-3 text-body text-text outline-none transition-shadow duration-150 ease-smooth placeholder:text-text-3 focus-visible:shadow-[0_0_0_3px_var(--color-ring)]",
        className
      )}
      {...props}
    />
  )
}

export { Input }
