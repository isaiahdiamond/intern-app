import type { ReactNode } from "react"

export default function Page({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <>
      <h1 className="text-title text-text">{title}</h1>
      <div className="mt-6">{children}</div>
    </>
  )
}
