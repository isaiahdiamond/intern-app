import { NavLink } from "react-router-dom";
import { paths } from "@/lib/icons";
import { Icon } from "./Icon";

const items = [
  { to: "/", label: "Dashboard", path: paths.dash },
  { to: "/listings", label: "All listings", path: paths.listings },
  { to: "/tracker", label: "Tracker", path: paths.tracker },
  { to: "/chat", label: "Coach", path: paths.coach },
];

export default function Rail({ online }: { online: boolean }) {
  return (
    <aside className="rail flex flex-col items-center py-4">
      <div className="flex size-10 items-center justify-center rounded-full bg-white font-mono text-[17px] font-semibold text-ink">
        i
      </div>

      <nav className="mt-8 flex w-full flex-col items-center gap-2">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            title={item.label}
            aria-label={item.label}
            className={({ isActive }) =>
              [
                "rail-item flex size-11 items-center justify-center rounded-md transition-colors",
                isActive
                  ? "bg-rail-active text-white"
                  : "text-white/45 hover:bg-rail-hover hover:text-white/80",
              ].join(" ")
            }
          >
            {({ isActive }) => (
              <>
                <Icon
                  path={item.path}
                  size={20}
                  stroke={isActive ? 2.1 : 1.5}
                />
                <span className="rail-tip" aria-hidden="true">
                  {item.label}
                </span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <span
        role="img"
        aria-label={online ? "API online" : "API offline"}
        title={online ? "API online" : "API offline"}
        className="mt-auto mb-2 size-2 rounded-full"
        style={{
          background: online ? "var(--color-online)" : "var(--color-offline)",
        }}
      />
    </aside>
  );
}
