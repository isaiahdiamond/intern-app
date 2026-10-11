import { NavLink, useNavigate } from "react-router-dom"
import { paths } from "@/lib/icons"
import { Icon } from "./Icon"

const items = [
  { to: "/", label: "Dashboard", path: paths.dash, badge: "" },
  { to: "/listings", label: "All listings", path: paths.listings, badge: "listings" },
  { to: "/tracker", label: "Tracker", path: paths.tracker, badge: "tracked" },
  { to: "/chat", label: "Coach", path: paths.coach, badge: "" },
  { to: "/profile", label: "Profile", path: paths.profile, badge: "" },
]

export default function Sidebar({
  listings,
  tracked,
  roles,
  online,
}: {
  listings: number
  tracked: number
  roles: { name: string; count: number | null }[]
  online: boolean
}) {
  const navigate = useNavigate()
  const counts: Record<string, string> = {
    listings: listings ? listings.toLocaleString() : "",
    tracked: tracked ? String(tracked) : "",
  }

  return (
    <aside className="sidebar-blur relative z-2 flex h-full w-sidebar shrink-0 flex-col border-r border-line">
      <div className="flex h-[52px] items-center gap-2.5 px-[18px]">
        <div className="flex size-[22px] items-center justify-center rounded-sm bg-accent font-mono text-[12px] font-semibold text-white">
          i
        </div>
        <div className="text-[13.5px] font-semibold">intern-app</div>
        <div className="ml-auto font-mono text-[10.5px] text-text-4">v0.4</div>
      </div>

      <nav className="flex flex-col gap-px px-2.5 py-1">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              [
                "flex h-[30px] items-center gap-2.5 rounded-[7px] px-2.5",
                isActive
                  ? "bg-accent/[0.13] font-semibold text-accent-text"
                  : "text-text hover:bg-black/[0.04]",
              ].join(" ")
            }
          >
            <span className="opacity-90">
              <Icon path={item.path} />
            </span>
            <span>{item.label}</span>
            <span className="ml-auto font-mono text-[11px] text-text-4">
              {counts[item.badge] ?? ""}
            </span>
          </NavLink>
        ))}
      </nav>

      <div className="flex items-center justify-between px-5 pt-[22px] pb-1.5">
        <span className="text-[11.5px] font-semibold text-text-4">Target roles</span>
        <span
          onClick={() => navigate("/onboarding")}
          className="cursor-pointer text-[11.5px] text-accent-text"
        >
          Edit
        </span>
      </div>
      <div className="flex min-h-0 flex-col gap-px overflow-auto px-2.5">
        {roles.map((role) => (
          <div
            key={role.name}
            className="flex h-7 shrink-0 items-center gap-2.5 rounded-[7px] px-2.5 text-text-2"
          >
            <span className="size-1.5 shrink-0 rounded-full bg-[#AEAEB2]" />
            <span className="truncate">{role.name}</span>
            <span className="ml-auto font-mono text-[11px] text-text-4">
              {role.count === null ? "" : role.count.toLocaleString()}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-auto flex flex-col gap-1 border-t border-line-soft px-5 pt-3.5 pb-[18px] font-mono text-[11px] text-text-4">
        <div className="flex items-center gap-[7px]">
          <span
            className="size-1.5 rounded-full"
            style={{ background: online ? "var(--color-online)" : "var(--color-offline)" }}
          />
          {online ? "api connected" : "api unreachable"}
        </div>
        <div>{window.location.host}</div>
      </div>
    </aside>
  )
}
