import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { paths } from "@/lib/icons";
import { Icon } from "./Icon";

function initials(name: string) {
  const words = name.trim().split(/\s+/).filter(Boolean);
  if (words.length === 0) return "";
  return words
    .slice(0, 2)
    .map((word) => word[0].toUpperCase())
    .join("");
}

export default function ProfileMenu({ name }: { name: string }) {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const mark = initials(name);

  return (
    <div
      className="relative shrink-0"
      onKeyDown={(event) => {
        if (event.key === "Escape") setOpen(false);
      }}
    >
      <button
        type="button"
        onClick={() => setOpen(!open)}
        title={name || "Profile"}
        aria-label={name ? `Profile: ${name}` : "Profile"}
        aria-haspopup="menu"
        aria-expanded={open}
        className="flex size-8 items-center justify-center rounded-full bg-ink text-ink-inverse transition-colors hover:bg-black"
      >
        {mark ? (
          <span className="text-[11px] font-semibold">{mark}</span>
        ) : (
          <Icon path={paths.person} size={15} />
        )}
      </button>

      {open ? (
        <>
          <div className="fixed inset-0 z-30" onClick={() => setOpen(false)} />
          <div className="absolute top-10 right-0 z-40 w-56 animate-pop rounded-lg border border-line-strong bg-surface p-1 shadow-float">
            <div className="px-3 py-2">
              <div className="truncate text-row text-ink">
                {name || "No name saved"}
              </div>
              <div className="mt-0.5 truncate text-meta text-ink-3">
                This board, on this machine
              </div>
            </div>
            <button
              type="button"
              onClick={() => {
                setOpen(false);
                navigate("/settings");
              }}
              className="flex h-10 w-full items-center gap-3 rounded-md px-3 text-control text-ink hover:bg-hover"
            >
              <Icon path={paths.gear} />
              Profile &amp; settings
            </button>
            <button
              type="button"
              onClick={() => {
                setOpen(false);
                navigate("/onboarding");
              }}
              className="flex h-10 w-full items-center gap-3 rounded-md px-3 text-control text-ink hover:bg-hover"
            >
              <Icon path={paths.target} />
              Edit target roles
            </button>
            <div
              aria-disabled="true"
              title="There are no accounts in this app, so there is nothing to log out of."
              className="flex h-10 cursor-not-allowed items-center gap-3 rounded-md px-3 text-control text-ink-3 opacity-45"
            >
              <Icon path={paths.exit} />
              Log out
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
