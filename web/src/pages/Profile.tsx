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
  const degree = (options?.degrees ?? []).find(
    (item) => item.key === profile?.education,
  );
  const degreeLabel = degree ? degree.label : (profile?.education ?? "—");
  const suggestions = allRoles.filter((name) => !roles.includes(name));

  return (
    <Layout
      title="Profile"
      subtitle="What the board is ranked against."
      slot="profile"
    >
      <div className="flex max-w-[760px] flex-col gap-6">
        <div className="card overflow-hidden rounded-2xl">
          <div
            className="h-28 w-full"
            style={{
              background:
                "linear-gradient(90deg, #F0EDE9 0%, #F6F6F6 50%, #EFF1F3 100%)",
              boxShadow: "inset 0 -1px 0 var(--color-line)",
            }}
          />
          <div className="p-6">
            <div className="text-section text-ink">
              {profile?.school || "No school saved"}
            </div>
            <div className="mt-1 text-body text-ink-3">
              {profile?.major || "No major saved"}
            </div>
            <div className="mt-5 flex flex-col">
              <Row label="Degree">{degreeLabel}</Row>
              <Row label="Industries">
                {profile?.industries.length
                  ? profile.industries.join(" · ")
                  : "—"}
              </Row>
              <Row label="Updated">
                {profile ? fullDate(profile.updated_at) : "—"}
              </Row>
              <Row label="API host">
                <span className="font-mono text-meta text-ink-3">
                  {window.location.host}
                </span>
              </Row>
            </div>
          </div>
        </div>

        <Panel title="What you are looking for">
          <p className="mt-2 mb-5 text-body text-ink-3">
            The Dashboard shows the newest listings that match this. Everything
            stays on All listings either way.
          </p>

          <Row label="Your degree">
            <select
              value={education}
              onChange={(event) => setEducation(event.target.value)}
              className="h-10 min-w-[220px] rounded-md border border-line-strong bg-surface px-3 text-control text-ink outline-none"
            >
              <option value="">No preference</option>
              {(options?.degrees ?? []).map((item) => (
                <option key={item.key} value={item.key}>
                  {item.label}
                </option>
              ))}
            </select>
            <span className="ml-3 text-meta text-ink-3">
              {education
                ? "Postings asking for more than this are hidden"
                : "Nothing is hidden"}
            </span>
          </Row>

          <Row label="Looking for">
            <div className="flex flex-wrap gap-2">
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
                    className={[
                      "flex h-10 items-center rounded-full border px-4 text-control transition-colors",
                      on
                        ? "border-transparent bg-ink text-ink-inverse"
                        : "border-line-strong bg-surface text-ink hover:bg-hover",
                    ].join(" ")}
                  >
                    {item.label}
                  </button>
                );
              })}
            </div>
          </Row>
        </Panel>

        <Panel title="Target roles" count={roles.length}>
          <div className="mt-4 flex flex-wrap gap-2">
            {roles.map((name) => (
              <span
                key={name}
                className="flex h-10 items-center gap-2 rounded-full border border-line-strong bg-surface pr-2 pl-4 text-control text-ink"
              >
                {name}
                <button
                  type="button"
                  onClick={() =>
                    setRoles(roles.filter((item) => item !== name))
                  }
                  aria-label={`Remove ${name}`}
                  className="flex size-6 items-center justify-center rounded-full text-[15px] leading-none text-ink-3 hover:bg-hover"
                >
                  ×
                </button>
              </span>
            ))}
            {roles.length === 0 ? (
              <span className="text-body text-ink-3">
                No roles yet, so nothing is narrowed by role.
              </span>
            ) : null}
          </div>

          <div className="mt-5 flex items-center gap-2">
            <input
              value={typed}
              onChange={(event) => setTyped(event.target.value)}
              onKeyDown={(event) => event.key === "Enter" && addRole()}
              placeholder="Add a role, e.g. Quantitative Intern"
              aria-label="Add a role"
              className="h-10 flex-1 rounded-md border border-line bg-surface-sunk px-4 text-control text-ink outline-none"
            />
            <button
              type="button"
              onClick={addRole}
              disabled={!typed.trim()}
              className="h-10 rounded-full border border-line-strong bg-surface px-4 text-control text-ink hover:bg-hover disabled:cursor-not-allowed disabled:opacity-45"
            >
              Add
            </button>
          </div>

          {suggestions.length ? (
            <div className="mt-5 flex flex-wrap items-center gap-2">
              <span className="mr-1 text-label text-ink-3 uppercase">
                Removed
              </span>
              {suggestions.map((name) => (
                <button
                  key={name}
                  type="button"
                  onClick={() => setRoles([...roles, name])}
                  className="flex h-10 items-center rounded-full border border-dashed border-line-strong px-4 text-control text-ink-3 hover:bg-hover"
                >
                  + {name}
                </button>
              ))}
            </div>
          ) : null}
        </Panel>

        <div className="flex items-center gap-3 pb-6">
          <button
            type="button"
            onClick={save}
            className="h-10 rounded-full bg-ink px-4 text-control text-ink-inverse transition-colors hover:bg-black motion-safe:active:scale-[0.96]"
          >
            Save
          </button>
          {saved ? (
            <span className="animate-in text-body text-[#1E7A34]">Saved</span>
          ) : null}
          {error ? (
            <span className="animate-in text-body text-[#B3261E]">{error}</span>
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
    <div className="card rounded-2xl p-6">
      <div className="flex items-center gap-2">
        <span className="text-section text-ink">{title}</span>
        {count === undefined ? null : (
          <span className="font-mono text-meta text-ink-3 tabular-nums">
            {count}
          </span>
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
    <div className="grid min-h-14 items-center gap-4 border-t border-line-soft py-3 text-body text-ink-2 [grid-template-columns:120px_minmax(0,1fr)] first:border-t-0">
      <span className="text-label text-ink-3 uppercase">{label}</span>
      <div className="flex min-w-0 flex-wrap items-center">{children}</div>
    </div>
  );
}
