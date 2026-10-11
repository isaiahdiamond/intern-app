import { useEffect, useRef, useState } from "react"
import { useNavigate } from "react-router-dom"
import type { Filters, Profile } from "@/lib/api"
import { get } from "@/lib/api"

export default function Onboarding() {
  const navigate = useNavigate()
  const other = useRef<HTMLInputElement>(null)
  const [offered, setOffered] = useState<string[]>([])
  const [picked, setPicked] = useState<string[]>([])
  const [custom, setCustom] = useState<string[]>([])
  const [open, setOpen] = useState(false)
  const [text, setText] = useState("")

  useEffect(() => {
    async function load() {
      const filters = await get<Filters>("/api/filters")
      const profile = await get<Profile>("/api/profile")
      if (filters) setOffered(filters.roles)
      if (profile?.profile) setPicked(profile.profile.roles)
    }
    load()
  }, [])

  function toggle(role: string) {
    setPicked(picked.includes(role) ? picked.filter((name) => name !== role) : [...picked, role])
  }

  function addOther() {
    const name = text.trim()
    setOpen(false)
    setText("")
    if (!name) return
    if (!custom.includes(name)) setCustom([...custom, name])
    if (!picked.includes(name)) setPicked([...picked, name])
  }

  const chips = [...offered, ...custom.filter((name) => !offered.includes(name))]

  return (
    <div className="relative flex h-screen flex-col overflow-auto">
      <div className="glow pointer-events-none absolute inset-x-0 top-0 h-[320px]" />

      <div className="relative flex h-14 items-center gap-2.5 px-7">
        <div className="flex size-[22px] items-center justify-center rounded-sm bg-accent font-mono text-[12px] font-semibold text-white">
          i
        </div>
        <div className="text-[13.5px] font-semibold">intern-app</div>
        <div className="ml-auto font-mono text-[11px] text-text-4">{window.location.host}</div>
      </div>

      <div className="relative flex flex-1 justify-center px-8 pt-[72px] pb-12">
        <div className="flex w-full max-w-[680px] flex-col">
          <div className="flex items-center gap-3">
            <span className="h-[3px] w-7 rounded-[2px] bg-accent" />
            <span className="font-mono text-[11.5px] text-text-4">target roles</span>
          </div>

          <h1 className="mt-[22px] mb-0 text-[34px] leading-[1.12] font-semibold tracking-[-0.025em]">
            Which roles are you looking for?
          </h1>
          <p className="mt-2.5 mb-0 max-w-[520px] text-[15px] leading-[1.5] text-text-3 text-pretty">
            Every morning the agent searches the job APIs for new listings in these roles and ranks
            them by your preferred industries.
          </p>

          <div className="mt-10 flex flex-col gap-[26px]">
            <div>
              <div className="mb-2.5 text-[12px] font-semibold text-text-4">
                Roles in your profile
              </div>
              <div className="flex flex-wrap gap-2">
                {chips.map((role) => {
                  const on = picked.includes(role)
                  return (
                    <button
                      type="button"
                      key={role}
                      onClick={() => toggle(role)}
                      className="box-border flex h-9 items-center rounded-[18px] border px-4 text-[14px] font-medium transition-colors duration-150 active:scale-[0.97]"
                      style={{
                        background: on ? "#0A84FF" : "#fff",
                        color: on ? "#fff" : "#1D1D1F",
                        borderColor: on ? "#0A84FF" : "rgba(0,0,0,0.1)",
                      }}
                    >
                      {role}
                    </button>
                  )
                })}

                {open ? (
                  <div className="box-border flex h-9 animate-in items-center gap-1.5 rounded-[18px] border border-accent bg-surface pr-1 pl-4 shadow-[0_0_0_3px_rgba(10,132,255,0.18)]">
                    <input
                      ref={other}
                      value={text}
                      onChange={(event) => setText(event.target.value)}
                      onKeyDown={(event) => {
                        if (event.key === "Enter") addOther()
                        if (event.key === "Escape") {
                          setOpen(false)
                          setText("")
                        }
                      }}
                      placeholder="Role name"
                      className="w-[150px] border-0 bg-transparent text-[14px] outline-none"
                    />
                    <button
                      type="button"
                      onClick={addOther}
                      className="flex h-7 items-center rounded-[14px] bg-accent px-3 text-[13px] font-medium text-white"
                    >
                      Add
                    </button>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => {
                      setOpen(true)
                      setTimeout(() => other.current?.focus(), 0)
                    }}
                    className="box-border flex h-9 items-center gap-1.5 rounded-[18px] border border-dashed border-black/20 bg-transparent px-4 text-[14px] font-medium text-text-2 hover:bg-black/[0.03]"
                  >
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth={1.6}>
                      <path d="M6 2v8M2 6h8" strokeLinecap="round" />
                    </svg>
                    Other
                  </button>
                )}
              </div>
            </div>
          </div>

          <div className="mt-14 flex items-center gap-3 border-t border-line pt-5">
            <span className="font-mono text-[12px] text-text-2">{picked.length} selected</span>
            <button
              type="button"
              onClick={() => navigate("/")}
              className="ml-auto flex h-[34px] items-center rounded-[9px] px-4 text-[13.5px] font-medium text-text-2 hover:bg-black/[0.04]"
            >
              Back
            </button>
            <button
              type="button"
              onClick={() => navigate("/")}
              disabled={picked.length === 0}
              className="flex h-[34px] items-center rounded-[9px] bg-accent px-5 text-[13.5px] font-medium text-white transition-opacity duration-150 disabled:opacity-40"
            >
              Continue
            </button>
          </div>
          <div className="mt-3 font-mono text-[11px] text-text-4">
            The API has no profile write endpoint yet, so changes here are not saved.
          </div>
        </div>
      </div>
    </div>
  )
}
