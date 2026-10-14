import { useEffect, useState } from "react";
import type { Filters, Listing, Page } from "@/lib/api";
import { ago, get, saveStatus, status, statuses } from "@/lib/api";
import Attribution from "@/components/Attribution";
import DetailPanel from "@/components/DetailPanel";
import { External, Magnifier } from "@/components/Icon";
import FilterMenu from "@/components/FilterMenu";
import type { Option } from "@/components/FilterMenu";
import Layout from "@/components/Layout";
import { ColumnHead, CompanyCell, RoleCell } from "@/components/Row";
import { StatusMenu, StatusPill } from "@/components/StatusPill";

const perPage = 50;

const levelLabels: Record<string, string> = {
  intern: "Intern",
  coop: "Co-op",
  new_grad: "New grad",
  other: "Other",
};

const educationLabels: Record<string, string> = {
  phd: "PhD",
  masters: "Master's",
  undergrad: "Bachelor's",
  any: "No degree stated",
};

export default function Listings() {
  const [filters, setFilters] = useState<Filters | null>(null);
  const [typed, setTyped] = useState("");
  const [query, setQuery] = useState("");
  const [industry, setIndustry] = useState("");
  const [roles, setRoles] = useState<string[]>([]);
  const [levels, setLevels] = useState<string[]>([]);
  const [educations, setEducations] = useState<string[]>([]);
  const [shown, setShown] = useState<string[]>([]);
  const [sort, setSort] = useState("newest");
  const [rows, setRows] = useState<Listing[]>([]);
  const [total, setTotal] = useState(0);
  const [more, setMore] = useState(false);
  const [page, setPage] = useState(1);
  const [menu, setMenu] = useState<string | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    async function load() {
      setFilters(await get<Filters>("/api/filters"));
    }
    load();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => setQuery(typed.trim()), 250);
    return () => clearTimeout(timer);
  }, [typed]);

  function url(wanted: number) {
    if (query) {
      const params = new URLSearchParams({
        q: query,
        industry,
        page: String(wanted),
        per_page: String(perPage),
      });
      return `/api/search?${params}`;
    }
    const params = new URLSearchParams({
      industry,
      sort,
      page: String(wanted),
      per_page: String(perPage),
    });
    for (const role of roles) params.append("role", role);
    for (const level of levels) params.append("level", level);
    for (const education of educations) params.append("education", education);
    for (const key of shown) params.append("status", key);
    return `/api/listings?${params}`;
  }

  useEffect(() => {
    async function load() {
      const result = await get<Page>(url(1));
      setPage(1);
      setRows(result ? result.listings : []);
      setTotal(result ? result.total : 0);
      setMore(result ? result.has_more : false);
      setLoaded(true);
    }
    load();
    // `url` is rebuilt every render, so depending on it would reload forever.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, industry, roles, levels, educations, shown, sort]);

  async function loadMore() {
    const result = await get<Page>(url(page + 1));
    if (!result) return;
    setPage(page + 1);
    setRows([...rows, ...result.listings]);
    setMore(result.has_more);
  }

  async function move(id: number, next: string) {
    const saved = await saveStatus(id, next);
    setMenu(null);
    if (!saved) return;
    if (filters)
      setFilters({ ...filters, board_status_counts: saved.board_counts });
    const leaves = shown.length ? !shown.includes(next) : next === "hidden";
    if (leaves) {
      setRows(rows.filter((row) => row.id !== id));
      setTotal(total - 1);
      if (selected === id) setSelected(null);
      return;
    }
    setRows(
      rows.map((row) => (row.id === id ? { ...row, status: next } : row)),
    );
  }

  function step(by: number) {
    const index = rows.findIndex((row) => row.id === selected);
    const row = rows[Math.min(Math.max(index + by, 0), rows.length - 1)];
    if (row) setSelected(row.id);
  }

  const current = rows.find((row) => row.id === selected) ?? null;
  const panelOpen = current !== null;
  const searching = query !== "";

  const industryOptions: Option[] = (filters?.industries ?? []).map((name) => ({
    key: name,
    label: name,
    count: filters?.industry_counts[name] ?? null,
    on: industry === name,
  }));
  const roleOptions: Option[] = (filters?.roles ?? []).map((name) => ({
    key: name,
    label: name,
    count: null,
    on: roles.includes(name),
  }));
  const levelOptions: Option[] = Object.keys(filters?.level_counts ?? {})
    .filter((key) => key !== "")
    .map((key) => ({
      key,
      label: levelLabels[key] ?? key,
      count: filters?.level_counts[key] ?? null,
      on: levels.includes(key),
    }));
  const educationOptions: Option[] = Object.keys(
    filters?.education_counts ?? {},
  )
    .filter((key) => key !== "")
    .map((key) => ({
      key,
      label: educationLabels[key] ?? key,
      count: filters?.education_counts[key] ?? null,
      on: educations.includes(key),
    }));
  const sortOptions: Option[] = (filters?.sorts ?? []).map((key) => ({
    key,
    label: key,
    count: null,
    on: sort === key,
  }));
  const statusOptions: Option[] = statuses.map((item) => ({
    key: item.key,
    label: item.key === "hidden" ? "Ignored" : item.label,
    count: filters?.board_status_counts?.[item.key] ?? 0,
    on: shown.includes(item.key),
  }));

  const dirty =
    industry !== "" ||
    roles.length > 0 ||
    levels.length > 0 ||
    educations.length > 0 ||
    shown.length > 0;
  const columns = panelOpen
    ? "minmax(160px,1fr) minmax(0,1.6fr) 0 112px 44px"
    : "minmax(220px,1.1fr) minmax(0,2.4fr) 120px 112px 44px";

  return (
    <Layout
      title="All listings"
      subtitle="Everything the sources have collected, newest first."
      slot="listings"
      panel={
        current ? (
          <DetailPanel
            listing={current}
            position={`${status(current.status).label.toLowerCase()} · ${rows.findIndex((row) => row.id === current.id) + 1} of ${rows.length}`}
            onPrev={() => step(-1)}
            onNext={() => step(1)}
            onClose={() => setSelected(null)}
            onStatus={(next) => move(current.id, next)}
          />
        ) : null
      }
    >
      <div onClick={() => setMenu(null)} className="card rounded-2xl p-3">
        <div className="flex min-h-16 flex-wrap items-center gap-x-3 gap-y-3 px-3 py-3">
          <FilterMenu
            label="Industry"
            value={industry}
            open={menu === "industry"}
            active={industry !== ""}
            options={industryOptions}
            onToggle={() => setMenu(menu === "industry" ? null : "industry")}
            onPick={(key) => setIndustry(industry === key ? "" : key)}
          />
          <FilterMenu
            label="Role"
            value={
              roles.length === 1
                ? roles[0]
                : roles.length
                  ? `${roles.length} selected`
                  : ""
            }
            open={menu === "role"}
            active={roles.length > 0}
            muted={searching}
            options={roleOptions}
            onToggle={() => setMenu(menu === "role" ? null : "role")}
            onPick={(key) =>
              setRoles(
                roles.includes(key)
                  ? roles.filter((name) => name !== key)
                  : [...roles, key],
              )
            }
          />
          <FilterMenu
            label="Level"
            value={
              levels.length === 1
                ? (levelLabels[levels[0]] ?? levels[0])
                : levels.length
                  ? `${levels.length} selected`
                  : ""
            }
            open={menu === "level"}
            active={levels.length > 0}
            muted={searching}
            options={levelOptions}
            onToggle={() => setMenu(menu === "level" ? null : "level")}
            onPick={(key) =>
              setLevels(
                levels.includes(key)
                  ? levels.filter((name) => name !== key)
                  : [...levels, key],
              )
            }
          />
          <FilterMenu
            label="Degree"
            value={
              educations.length === 1
                ? (educationLabels[educations[0]] ?? educations[0])
                : educations.length
                  ? `${educations.length} selected`
                  : ""
            }
            open={menu === "education"}
            active={educations.length > 0}
            muted={searching}
            options={educationOptions}
            onToggle={() => setMenu(menu === "education" ? null : "education")}
            onPick={(key) =>
              setEducations(
                educations.includes(key)
                  ? educations.filter((name) => name !== key)
                  : [...educations, key],
              )
            }
          />
          <FilterMenu
            label="Status"
            value={
              shown.length === 1
                ? (statusOptions.find((item) => item.key === shown[0])?.label ??
                  shown[0])
                : shown.length
                  ? `${shown.length} selected`
                  : ""
            }
            open={menu === "status"}
            active={shown.length > 0}
            muted={searching}
            options={statusOptions}
            onToggle={() => setMenu(menu === "status" ? null : "status")}
            onPick={(key) =>
              setShown(
                shown.includes(key)
                  ? shown.filter((name) => name !== key)
                  : [...shown, key],
              )
            }
          />
          <FilterMenu
            label="Sort"
            value={sort}
            open={menu === "sort"}
            active={sort !== "newest"}
            muted={searching}
            options={sortOptions}
            onToggle={() => setMenu(menu === "sort" ? null : "sort")}
            onPick={(key) => {
              setSort(key);
              setMenu(null);
            }}
          />
          {dirty ? (
            <button
              type="button"
              onClick={() => {
                setIndustry("");
                setRoles([]);
                setLevels([]);
                setEducations([]);
                setShown([]);
              }}
              className="h-10 rounded-full px-3 text-control text-ink-3 whitespace-nowrap hover:bg-hover"
            >
              Clear
            </button>
          ) : null}

          <div className="ml-auto box-border flex h-10 max-w-[300px] min-w-[200px] flex-[1_1_200px] items-center gap-2 rounded-full border border-line bg-surface-sunk px-4">
            <Magnifier />
            <input
              value={typed}
              onChange={(event) => setTyped(event.target.value)}
              placeholder="Search roles, companies"
              aria-label="Search roles, companies"
              className="min-w-0 flex-1 border-0 bg-transparent text-control text-ink outline-none"
            />
          </div>
        </div>

        <div className="px-3 pb-3 font-mono text-meta text-ink-3">
          {rows.length.toLocaleString()} of {total.toLocaleString()}
          {searching ? " · searching every listing" : ""}
        </div>

        <ColumnHead
          columns={columns}
          labels={["Company", "Role", "Posted", "Status", ""]}
        />

        {rows.map((listing) => {
          const isTracked = listing.status !== "new";
          return (
            <div
              key={listing.id}
              onClick={() => setSelected(listing.id)}
              className="group relative grid cursor-pointer items-center gap-4 border-t border-line-soft pr-4 pl-6 transition-colors duration-[var(--duration-hover)] hover:bg-row-hover"
              style={{
                gridTemplateColumns: columns,
                height: "var(--row-h)",
                background:
                  selected === listing.id ? "var(--color-selected)" : undefined,
              }}
            >
              {selected === listing.id ? (
                <span className="absolute top-1/2 left-0 h-10 w-[2px] -translate-y-1/2 bg-ink" />
              ) : null}
              {isTracked ? null : (
                <span className="absolute top-1/2 left-2 size-1.5 -translate-y-1/2 rounded-full bg-accent" />
              )}
              <CompanyCell listing={listing} />
              <RoleCell listing={listing} bold={!isTracked} />
              <span className="truncate font-mono text-meta text-ink-3">
                {panelOpen ? "" : ago(listing.posted_at)}
              </span>
              <div className="flex justify-start">
                <StatusPill
                  value={listing.status}
                  chevron
                  onClick={(event) => {
                    event.stopPropagation();
                    setMenu(
                      menu === `row${listing.id}` ? null : `row${listing.id}`,
                    );
                  }}
                />
              </div>
              <a
                href={listing.url}
                target="_blank"
                rel="noreferrer"
                onClick={(event) => event.stopPropagation()}
                title="Open the original listing"
                aria-label="Open the original listing"
                className="flex size-9 items-center justify-center rounded-full text-ink-3 opacity-0 transition-opacity hover:bg-hover focus-visible:opacity-100 group-hover:opacity-100"
              >
                <External size={14} />
              </a>
              {menu === `row${listing.id}` ? (
                <StatusMenu
                  value={listing.status}
                  includeNew
                  onPick={(next) => move(listing.id, next)}
                  style={{ right: 56, top: 48 }}
                />
              ) : null}
            </div>
          );
        })}

        {loaded && rows.length === 0 ? (
          <div className="animate-in px-4 py-12 text-center text-lead text-ink-2">
            No listings match these filters.
          </div>
        ) : null}

        {more ? (
          <div className="flex justify-center border-t border-line-soft p-4">
            <button
              type="button"
              onClick={loadMore}
              className="h-10 rounded-full border border-line-strong bg-surface px-4 text-control text-ink hover:bg-hover"
            >
              Load {perPage} more
            </button>
          </div>
        ) : null}
      </div>

      <Attribution listings={rows} />
    </Layout>
  );
}
