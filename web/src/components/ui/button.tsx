import { cva, type VariantProps } from "class-variance-authority"
import { Slot } from "radix-ui"
import type { ComponentProps } from "react"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex h-8 shrink-0 items-center justify-center gap-2 whitespace-nowrap rounded-control text-body font-medium transition-colors duration-150 ease-smooth outline-none focus-visible:shadow-[0_0_0_3px_var(--color-ring)] disabled:pointer-events-none disabled:opacity-40 [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        primary: "bg-accent px-4 text-white hover:bg-accent-hover",
        secondary: "border border-line bg-surface px-4 text-text hover:bg-hover",
        ghost: "px-3 text-text-2 hover:bg-hover hover:text-text",
      },
      size: {
        default: "",
        icon: "w-8 px-0",
      },
    },
    defaultVariants: {
      variant: "secondary",
      size: "default",
    },
  }
)

type ButtonProps = ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & { asChild?: boolean }

function Button({ className, variant, size, asChild, ...props }: ButtonProps) {
  const Tag = asChild ? Slot.Root : "button"
  return <Tag className={cn(buttonVariants({ variant, size }), className)} {...props} />
}

export { Button, buttonVariants }
