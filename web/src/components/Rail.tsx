import { NavLink, useNavigate } from "react-router-dom";
import { paths } from "@/lib/icons";
import { Icon } from "./Icon";

const items = [
  { to: "/", label: "Dashboard", path: paths.dash },
  { to: "/listings", label: "All listings", path: paths.listings },
  { to: "/tracker", label: "Tracker", path: paths.tracker },
  { to: "/chat", label: "Coach", path: paths.coach },
  { to: "/profile", label: "Profile", path: paths.profile },
];

export default function Rail({ online }: { online: boolean }) {
  const navigate = useNavigate();

  return (
    <aside className="rail flex flex-col items-center py-4">
      <div className="flex size-10 items-center justify-center rounded-md bg-white/10 font-mono text-[16px] font-semibold text-ink-inverse">
        i
      </div>

      <nav className="mt-6 flex w-full flex-col items-center gap-2">
        {items.map((item) => (
          <div key={item.to} className="relative flex w-full justify-center">
            <NavLink
              to={item.to}
              end={item.to === "/"}
              title={item.label}
              aria-label={item.label}
              className={({ isActive }) =>
                [
                  "flex size-11 items-center justify-center rounded-md transition-colors",
                  isActive
                    ? "bg-rail-active text-ink-inverse"
                    : "text-ink-4 hover:bg-rail-hover hover:text-ink-inverse",
                ].join(" ")
              }
            >
              {({ isActive }) => (
                <>
                  <Icon
                    path={item.path}
                    size={20}
                    stroke={isActive ? 2 : 1.5}
                  />
                  {isActive ? (
                    <span className="absolute top-1/2 left-0 h-5 w-[3px] -translate-y-1/2 rounded-full bg-ink-inverse" />
                  ) : null}
                </>
              )}
            </NavLink>
          </div>
        ))}

        <button
          type="button"
          onClick={() => navigate("/tracker", { state: { add: true } })}
          title="Add a job"
          aria-label="Add a job"
          className="flex size-11 items-center justify-center rounded-md text-ink-4 transition-colors hover:bg-rail-hover hover:text-ink-inverse"
        >
          <Icon path={paths.add} size={20} />
        </button>
      </nav>

      <div className="mt-auto flex flex-col items-center gap-4">
        <NavLink
          to="/profile"
          title="Settings"
          aria-label="Settings"
          className="flex size-11 items-center justify-center rounded-md text-ink-4 transition-colors hover:bg-rail-hover hover:text-ink-inverse"
        >
          <Icon path={paths.gear} size={20} />
        </NavLink>
        <span
          role="img"
          aria-label={online ? "API online" : "API offline"}
          title={online ? "API online" : "API offline"}
          className="size-2 rounded-full"
          style={{
            background: online ? "var(--color-online)" : "var(--color-offline)",
          }}
        />
      </div>
    </aside>
  );
}
