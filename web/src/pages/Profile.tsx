import { useEffect, useState } from "react";
import type { Filters, Profile as ProfileData } from "@/lib/api";
import { fullDate, get } from "@/lib/api";
import Layout from "@/components/Layout";

type Option = { key: string; label: string };
type Options = { degrees: Option[]; seeking: Option[] };

export default function Profile() {
  const [data, setData] = useState<ProfileData | null>(null);
  const [options, setOptions] = useState<Options | null>(null);
  const [allRoles, setAllRoles] = useState<string[]>([]);

  const [education, setEducation] = useState("");
  const [seeking, setSeeking] = useState<string[]>([]);
  const [roles, setRoles] = useState<string[]>([]);
  const [typed, setTyped] = useState("");
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      const profile = await get<ProfileData>("/api/profile");
      const choices = await get<Options>("/api/options");
      const filters = await get<Filters>("/api/filters");
      setData(profile);
      setOptions(choices);
      if (filters) setAllRoles(filters.roles);
      if (profile?.profile) {
        setEducation(profile.profile.education);
        setSeeking(profile.profile.seeking);
        setRoles(profile.profile.roles);
      }
    }
    load();
  }, []);

  async function save() {
    setError("");
    let response: Response | null = null;
    try {
      response = await fetch("/api/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ education, seeking, roles }),
      });
    } catch {
      response = null;
    }
    if (!response || !response.ok) {
      setError("Could not save that.");
      return;
    }
    setData(await response.json());
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  function addRole() {
    const name = typed.trim();
    if (name && !roles.includes(name)) setRoles([...roles, name]);
    setTyped("");
  }

  const profile = data?.profile;
  const suggestions = allRoles.filter((name) => !roles.includes(name));

  return (
    <Layout title="Profile">
      <div className="flex max-w-[680px] flex-col gap-4">
        <Panel title="What you are looking for">
          <p className="px-4 pt-3.5 text-[12.5px] leading-[1.5] text-text-3">
            The Dashboard shows the newest listings that match this. Everything
            stays on All listings either way.
          </p>

          <Row label="Your degree">
            <select
              value={education}
              onChange={(event) => setEducation(event.target.value)}
              className="h-[30px] min-w-[200px] rounded-control border border-line bg-surface px-2 text-[13px] outline-none"
            >
              <option value="">No preference</option>
              {(options?.degrees ?? []).map((item) => (
                <option key={item.key} value={item.key}>
                  {item.label}
                </option>
              ))}
            </select>
            <span className="ml-2.5 text-[12px] text-text-4">
              {education
                ? "Postings asking for more than this are hidden"
                : "Nothing is hidden"}
            </span>
          </Row>

          <Row label="Looking for">
            <div className="flex flex-wrap gap-1.5">
              {(options?.seeking ?? []).map((item) => {
                const on = seeking.includes(item.key);
                return (
                  <button
                    key={item.key}
                    type="button"
                    onClick={() =>
                      setSeeking(
                        on
                          ? seeking.filter((name) => name !== item.key)
                          : [...seeking, item.key],
                      )
                    }
                    className="flex h-[26px] items-center rounded-control px-2.5 text-[12.5px] font-medium"
                    style={{
                      background: on ? "rgba(10,132,255,0.13)" : "transparent",
                      color: on ? "#0066CC" : "#3A3A3C",
                      border: on ? "none" : "1px solid var(--color-line)",
                    }}
                  >
                    {item.label}
                  </button>
                );
              })}
            </div>
          </Row>
        </Panel>

        <Panel title="Target roles" count={roles.length}>
          <div className="flex flex-wrap gap-1.5 px-4 py-3.5">
            {roles.map((name) => (
              <span
                key={name}
                className="flex h-[26px] items-center gap-1.5 rounded-control border border-line bg-black/[0.02] pr-1.5 pl-2.5 text-[12.5px]"
              >
                {name}
                <button
                  type="button"
                  onClick={() =>
                    setRoles(roles.filter((item) => item !== name))
                  }
                  className="flex size-[16px] items-center justify-center rounded-full text-[13px] leading-none text-text-4 hover:bg-black/[0.06]"
                >
                  ×
                </button>
              </span>
            ))}
            {roles.length === 0 ? (
              <span className="text-[12.5px] text-text-4">
                No roles yet, so nothing is narrowed by role.
              </span>
            ) : null}
          </div>

          <div className="flex items-center gap-2 border-t border-line-soft px-4 py-3">
            <input
              value={typed}
              onChange={(event) => setTyped(event.target.value)}
              onKeyDown={(event) => event.key === "Enter" && addRole()}
              placeholder="Add a role, e.g. Quantitative Intern"
              className="h-[30px] flex-1 rounded-control border border-line bg-surface px-2.5 text-[13px] outline-none"
            />
            <button
              type="button"
              onClick={addRole}
              disabled={!typed.trim()}
              className="h-[30px] rounded-control border border-line px-3 text-[13px] font-medium text-text-2 hover:bg-hover disabled:opacity-40"
            >
              Add
            </button>
          </div>

          {suggestions.length ? (
            <div className="flex flex-wrap items-center gap-1.5 border-t border-line-soft px-4 py-3">
              <span className="mr-1 text-[11px] font-medium tracking-[0.04em] text-text-5 uppercase">
                Removed
              </span>
              {suggestions.map((name) => (
                <button
                  key={name}
                  type="button"
                  onClick={() => setRoles([...roles, name])}
                  className="flex h-[24px] items-center rounded-control border border-dashed border-line px-2.5 text-[12.5px] text-text-3 hover:bg-hover"
                >
                  + {name}
                </button>
              ))}
            </div>
          ) : null}
        </Panel>

        <Panel title="You">
          <Row label="School">{profile?.school || "—"}</Row>
          <Row label="Major">{profile?.major || "—"}</Row>
          <Row label="Industries">
            {profile?.industries.length ? profile.industries.join(" · ") : "—"}
          </Row>
          <Row label="Updated">
            {profile ? fullDate(profile.updated_at) : "—"}
          </Row>
        </Panel>

        <div className="flex items-center gap-3 pb-6">
          <button
            type="button"
            onClick={save}
            className="h-[30px] rounded-control bg-accent px-3.5 text-[13px] font-medium text-white hover:bg-accent-hover"
          >
            Save
          </button>
          {saved ? (
            <span className="text-[12.5px] text-[#1E7A34]">Saved</span>
          ) : null}
          {error ? (
            <span className="text-[12.5px] text-[#B3261E]">{error}</span>
          ) : null}
        </div>
      </div>
    </Layout>
  );
}

function Panel({
  title,
  count,
  children,
}: {
  title: string;
  count?: number;
  children: React.ReactNode;
}) {
  return (
    <div className="overflow-hidden rounded-panel border border-line bg-surface">
      <div className="flex h-[46px] items-center gap-2 border-b border-line-soft px-4">
        <span className="text-[13px] font-semibold">{title}</span>
        {count === undefined ? null : (
          <span className="font-mono text-[11.5px] text-text-4">{count}</span>
        )}
      </div>
      {children}
    </div>
  );
}

function Row({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="grid min-h-[46px] items-center gap-4 border-t border-line-soft px-4 py-2.5 text-[13px] [grid-template-columns:140px_minmax(0,1fr)] first:border-t-0">
      <span className="text-[12.5px] text-text-3">{label}</span>
      <div className="flex min-w-0 flex-wrap items-center">{children}</div>
    </div>
  );
}
