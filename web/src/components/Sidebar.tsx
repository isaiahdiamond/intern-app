import { NavLink } from "react-router-dom"
import { Bookmark } from "lucide-react"
import { nav } from "./nav"

export default function Sidebar() {
  return (
    <aside className="sidebar-blur fixed inset-y-0 left-0 hidden w-sidebar flex-col border-r border-line px-3 py-4 lg:flex">
      <div className="px-2 pb-5 text-section">intern-app</div>

      <nav className="flex flex-col gap-0.5">
        {nav.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              [
                "flex h-8 items-center gap-2.5 rounded-pill px-2 text-body transition-colors duration-150 ease-smooth",
                isActive ? "bg-selected font-medium text-accent-text" : "text-text-2 hover:bg-hover hover:text-text",
              ].join(" ")
            }
          >
            {({ isActive }) => (
              <>
                <item.icon size={15} className={isActive ? "text-accent" : "text-text-3"} />
                {item.label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="mt-6 px-2 pb-1 text-group text-text-3">Saved searches</div>
      <div className="flex flex-col gap-0.5">
        <div className="flex h-8 items-center gap-2.5 rounded-pill px-2 text-body text-text-3">
          <Bookmark size={15} />
          None yet
        </div>
      </div>
    </aside>
  )
}
