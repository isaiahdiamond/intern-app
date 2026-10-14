import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Filters, Profile } from "@/lib/api";
import { get } from "@/lib/api";

export default function Onboarding() {
  const navigate = useNavigate();
  const other = useRef<HTMLInputElement>(null);
  const [offered, setOffered] = useState<string[]>([]);
  const [picked, setPicked] = useState<string[]>([]);
  const [custom, setCustom] = useState<string[]>([]);
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("");
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    async function load() {
      const filters = await get<Filters>("/api/filters");
      const profile = await get<Profile>("/api/profile");
      if (filters) setOffered(filters.roles);
      if (profile?.profile) setPicked(profile.profile.roles);
      setLoaded(true);
    }
    load();
  }, []);

  function toggle(role: string) {
    setPicked(
      picked.includes(role)
        ? picked.filter((name) => name !== role)
        : [...picked, role],
    );
  }

  function addOther() {
    const name = text.trim();
    setOpen(false);
    setText("");
    if (!name) return;
    if (!custom.includes(name)) setCustom([...custom, name]);
    if (!picked.includes(name)) setPicked([...picked, name]);
  }

  const chips = [
    ...offered,
    ...custom.filter((name) => !offered.includes(name)),
  ];

  return (
    <div className="relative z-1 h-screen overflow-y-auto overscroll-contain">
      <div className="mx-auto flex w-full max-w-[760px] flex-col px-10 pt-16 pb-12">
        <div className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-md bg-ink font-mono text-[16px] font-semibold text-ink-inverse">
            i
          </div>
          <span
            className="font-mono text-meta"
            style={{ color: "var(--title-ink-2)" }}
          >
            target roles
          </span>
        </div>

        <h1
          className="mt-10 mb-0 text-title-lg"
          style={{ color: "var(--title-ink)" }}
        >
          Which roles are you looking for?
        </h1>
        <p
          className="mt-3 mb-0 max-w-[560px] text-lead text-pretty"
          style={{ color: "var(--title-ink-2)" }}
        >
          Every morning the agent searches the job APIs for new listings in
          these roles and ranks them by your preferred industries.
        </p>

        <div className="card mt-10 rounded-2xl p-6">
          <div className="text-label text-ink-3 uppercase">
            Roles in your profile
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {loaded
              ? null
              : [200, 196, 172, 168, 244, 222, 232, 186].map((width) => (
                  <div
                    key={width}
                    aria-hidden="true"
                    className="skeleton h-11 rounded-full"
                    style={{ width }}
                  />
                ))}
            {loaded && chips.length === 0 ? (
              <div className="animate-in text-lead text-ink-2">
                No roles came back from the board. Add your own below.
              </div>
            ) : null}
            {chips.map((role) => {
              const on = picked.includes(role);
              return (
                <button
                  type="button"
                  key={role}
                  onClick={() => toggle(role)}
                  className={[
                    "box-border flex h-11 items-center rounded-full border px-4 text-lead font-medium transition-[background-color,border-color,color,scale] ease-out motion-safe:active:scale-[0.96]",
                    on
                      ? "border-transparent bg-ink text-ink-inverse"
                      : "border-line-strong bg-surface text-ink hover:bg-hover",
                  ].join(" ")}
                  style={{ WebkitTapHighlightColor: "transparent" }}
                >
                  {role}
                </button>
              );
            })}

            {open ? (
              <div className="box-border flex h-11 animate-in items-center gap-2 rounded-full border border-ink bg-surface pr-1 pl-4">
                <input
                  ref={other}
                  value={text}
                  onChange={(event) => setText(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") addOther();
                    if (event.key === "Escape") {
                      setOpen(false);
                      setText("");
                    }
                  }}
                  placeholder="Role name"
                  aria-label="Role name"
                  className="w-[160px] border-0 bg-transparent text-lead text-ink outline-none"
                />
                <button
                  type="button"
                  onClick={addOther}
                  className="flex h-9 items-center rounded-full bg-ink px-4 text-control text-ink-inverse"
                >
                  Add
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={() => {
                  setOpen(true);
                  setTimeout(() => other.current?.focus(), 0);
                }}
                className="box-border flex h-11 items-center gap-2 rounded-full border border-dashed border-line-strong bg-transparent px-4 text-lead font-medium text-ink-2 hover:bg-hover"
              >
                + Other
              </button>
            )}
          </div>
        </div>

        <div className="card mt-10 flex items-center gap-3 rounded-2xl p-4">
          <span className="font-mono text-meta text-ink-2 tabular-nums">
            {picked.length} selected
          </span>
          <button
            type="button"
            onClick={() => navigate("/")}
            className="ml-auto flex h-10 items-center rounded-full px-4 text-control text-ink-3 hover:bg-hover"
          >
            Back
          </button>
          <button
            type="button"
            onClick={() => navigate("/")}
            disabled={picked.length === 0}
            className="flex h-10 items-center rounded-full bg-ink px-5 text-control text-ink-inverse transition-opacity disabled:cursor-not-allowed disabled:opacity-45 enabled:motion-safe:active:scale-[0.96]"
          >
            Continue
          </button>
        </div>
        <div
          className="mt-4 font-mono text-meta"
          style={{ color: "var(--title-ink-2)" }}
        >
          The API has no profile write endpoint yet, so changes here are not
          saved.
        </div>
      </div>
    </div>
  );
}
