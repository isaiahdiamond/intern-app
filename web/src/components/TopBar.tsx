import { NavLink } from "react-router-dom"
import { nav } from "./nav"

export default function TopBar() {
  return (
    <header className="sidebar-blur sticky top-0 z-10 flex items-center gap-4 border-b border-line px-5 py-2.5 lg:hidden">
      <span className="text-body font-medium">intern-app</span>
      <nav className="flex gap-1 overflow-x-auto">
        {nav.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              [
                "whitespace-nowrap rounded-pill px-2.5 py-1 text-body transition-colors duration-150 ease-smooth",
                isActive ? "bg-selected font-medium text-accent-text" : "text-text-2",
              ].join(" ")
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </header>
  )
}
