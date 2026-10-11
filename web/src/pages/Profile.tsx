import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import type { Profile as ProfileData } from "@/lib/api"
import { fullDate, get } from "@/lib/api"
import Layout from "@/components/Layout"

export default function Profile() {
  const navigate = useNavigate()
  const [data, setData] = useState<ProfileData | null>(null)

  useEffect(() => {
    async function load() {
      setData(await get<ProfileData>("/api/profile"))
    }
    load()
  }, [])

  const profile = data?.profile
  const fields = [
    { label: "School", value: profile?.school ?? "" },
    { label: "Major", value: profile?.major ?? "" },
    { label: "Onboarded", value: data?.onboarded ? "yes" : "no" },
    { label: "Updated", value: profile ? fullDate(profile.updated_at) : "" },
  ]

  const groups = [
    { title: "Target roles", items: profile?.roles ?? [] },
    { title: "Preferred industries", items: profile?.industries ?? [] },
  ]

  return (
    <Layout title="Profile">
      <div className="flex max-w-[640px] flex-col gap-4">
        <div className="overflow-hidden rounded-panel border border-line bg-surface">
          <div className="flex h-[46px] items-center border-b border-line-soft px-4 text-[13px] font-semibold">
            You
          </div>
          {fields.map((field, index) => (
            <div
              key={field.label}
              className="grid min-h-[46px] items-center gap-4 px-4 [grid-template-columns:140px_minmax(0,1fr)]"
              style={{ borderTop: index ? "1px solid rgba(0,0,0,0.06)" : "none" }}
            >
              <span className="text-[12.5px] text-text-3">{field.label}</span>
              <span className="text-[13px] break-words">{field.value || "—"}</span>
            </div>
          ))}
        </div>

        {groups.map((group) => (
          <div
            key={group.title}
            className="overflow-hidden rounded-panel border border-line bg-surface"
          >
            <div className="flex h-[46px] items-center gap-2 border-b border-line-soft px-4">
              <span className="text-[13px] font-semibold">{group.title}</span>
              <span className="font-mono text-[11.5px] text-text-4">{group.items.length}</span>
              {group.title === "Target roles" ? (
                <span
                  onClick={() => navigate("/onboarding")}
                  className="ml-auto cursor-pointer text-[12.5px] text-accent-text"
                >
                  Edit
                </span>
              ) : null}
            </div>
            <div className="flex flex-wrap gap-2 px-4 pt-3.5 pb-4">
              {group.items.map((item) => (
                <span
                  key={item}
                  className="box-border flex h-[30px] items-center rounded-control border border-line-strong bg-surface px-3 text-[12.5px] font-medium"
                >
                  {item}
                </span>
              ))}
            </div>
          </div>
        ))}

        <div className="px-1 font-mono text-[11px] text-text-4">
          Read-only: the API has no profile write endpoint yet.
        </div>
      </div>
    </Layout>
  )
}
