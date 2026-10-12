import { useEffect, useState } from "react";
import type { Filters, Listing, Page } from "@/lib/api";
import { ago, get, saveStatus, status } from "@/lib/api";
import Attribution from "@/components/Attribution";
import DetailPanel from "@/components/DetailPanel";
import { External, Magnifier } from "@/components/Icon";
import FilterMenu from "@/components/FilterMenu";
import type { Option } from "@/components/FilterMenu";
import Layout from "@/components/Layout";
import { ColumnHead, CompanyCell, RoleCell } from "@/components/Row";
import { StatusMenu } from "@/components/StatusPill";

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
  const [sort, setSort] = useState("newest");
  const [rows, setRows] = useState<Listing[]>([]);
  const [total, setTotal] = useState(0);
  const [more, setMore] = useState(false);
  const [page, setPage] = useState(1);
  const [menu, setMenu] = useState<string | null>(null);
  const [selected, setSelected] = useState<number | null>(null);

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
    return `/api/listings?${params}`;
  }

  useEffect(() => {
    async function load() {
      const result = await get<Page>(url(1));
      setPage(1);
      setRows(result ? result.listings : []);
      setTotal(result ? result.total : 0);
      setMore(result ? result.has_more : false);
    }
    load();
    // `url` is rebuilt every render, so depending on it would reload forever.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, industry, roles, levels, educations, sort]);

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

  const dirty =
    industry !== "" ||
    roles.length > 0 ||
    levels.length > 0 ||
    educations.length > 0;
  const columns = panelOpen
    ? "minmax(0,1fr) minmax(0,1.4fr) 56px 110px"
    : "minmax(140px,1fr) minmax(0,2.2fr) 72px 110px";

  return (
    <Layout
      title="All listings"
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
      <div
        onClick={() => setMenu(null)}
        className="rounded-panel border border-line bg-surface"
      >
        <div className="flex flex-wrap items-center gap-x-3 gap-y-2.5 border-b border-line-soft px-3.5 py-3">
          <div className="flex max-w-full min-w-0 shrink-0 flex-wrap items-center gap-2">
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
              onToggle={() =>
                setMenu(menu === "education" ? null : "education")
              }
              onPick={(key) =>
                setEducations(
                  educations.includes(key)
                    ? educations.filter((name) => name !== key)
                    : [...educations, key],
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
              <span
                onClick={() => {
                  setIndustry("");
                  setRoles([]);
                  setLevels([]);
                  setEducations([]);
                }}
                className="cursor-pointer px-1 text-[12.5px] whitespace-nowrap text-accent-text hover:underline"
              >
                Clear
              </span>
            ) : null}
            <span className="ml-1.5 truncate font-mono text-[11.5px] whitespace-nowrap text-text-4">
              {rows.length.toLocaleString()} of {total.toLocaleString()}
              {searching ? " · searching every listing" : ""}
            </span>
          </div>
          <div className="ml-auto box-border flex h-[30px] max-w-[260px] min-w-[180px] flex-[1_1_180px] items-center gap-[7px] rounded-control border border-line-soft bg-bg px-2.5">
            <Magnifier />
            <input
              value={typed}
              onChange={(event) => setTyped(event.target.value)}
              placeholder="Search roles, companies"
              className="min-w-0 flex-1 border-0 bg-transparent text-[12.5px] outline-none"
            />
          </div>
        </div>

        <ColumnHead
          columns={columns}
          labels={["Company", "Role", "Posted", "Track"]}
        />

        {rows.map((listing, index) => {
          const tracked = listing.status !== "new";
          const tone = status(listing.status);
          return (
            <div
              key={listing.id}
              onClick={() => setSelected(listing.id)}
              className="relative grid h-12 items-center gap-4 pr-3.5 pl-[30px] transition-colors duration-100 hover:bg-row-hover"
              style={{
                gridTemplateColumns: columns,
                borderTop: index === 0 ? "none" : "1px solid rgba(0,0,0,0.05)",
                background:
                  selected === listing.id
                    ? "rgba(10,132,255,0.07)"
                    : "transparent",
              }}
            >
              {tracked ? null : (
                <span className="absolute top-1/2 left-3 -mt-[3px] size-1.5 rounded-full bg-accent" />
              )}
              <CompanyCell listing={listing} />
              <RoleCell listing={listing} bold={!tracked} />
              <span className="font-mono text-[11.5px] whitespace-nowrap text-text-3">
                {ago(listing.posted_at)}
              </span>
              <div className="flex items-center justify-end gap-1.5">
                <div
                  onClick={(event) => {
                    event.stopPropagation();
                    if (tracked)
                      setMenu(
                        menu === `row${listing.id}` ? null : `row${listing.id}`,
                      );
                    else move(listing.id, "saved");
                  }}
                  title={
                    tracked ? `In tracker · ${tone.label}` : "Add to tracker"
                  }
                  className="flex size-7 items-center justify-center rounded-[7px] text-accent-text transition-colors duration-150 hover:brightness-95"
                  style={{
                    background: tracked ? tone.bg : "rgba(10,132,255,0.10)",
                  }}
                >
                  {tracked ? (
                    <span
                      className="size-[9px] rounded-full"
                      style={{ background: tone.dot }}
                    />
                  ) : (
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 12 12"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth={1.7}
                    >
                      <path d="M6 2v8M2 6h8" strokeLinecap="round" />
                    </svg>
                  )}
                </div>
                <a
                  href={listing.url}
                  target="_blank"
                  rel="noreferrer"
                  onClick={(event) => event.stopPropagation()}
                  title="Open the original listing"
                  className="box-border flex h-7 items-center gap-[5px] rounded-[7px] border border-line-strong bg-surface px-2.5 text-[12.5px] font-medium text-text no-underline hover:bg-bg hover:no-underline"
                >
                  Listing
                  <External />
                </a>
              </div>
              {menu === `row${listing.id}` ? (
                <StatusMenu
                  value={listing.status}
                  onPick={(next) => move(listing.id, next)}
                  style={{ right: 92, top: 40 }}
                />
              ) : null}
            </div>
          );
        })}

        {rows.length === 0 ? (
          <div className="px-4 py-10 text-center text-text-3">
            No listings match these filters.
          </div>
        ) : null}

        {more ? (
          <div className="flex justify-center border-t border-line-row p-3.5">
            <button
              type="button"
              onClick={loadMore}
              className="box-border flex h-[30px] items-center rounded-control border border-line-strong bg-surface px-3.5 text-[12.5px] font-medium hover:bg-bg"
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
