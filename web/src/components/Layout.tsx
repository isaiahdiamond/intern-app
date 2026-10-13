import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import type { Filters, Page } from "@/lib/api";
import { get, today, trackedTotal } from "@/lib/api";
import Sidebar from "./Sidebar";

export default function Layout({
  title,
  toolbar,
  panel,
  tight,
  children,
}: {
  title: string;
  toolbar?: ReactNode;
  panel?: ReactNode;
  tight?: boolean;
  children: ReactNode;
}) {
  const [listings, setListings] = useState(0);
  const [tracked, setTracked] = useState(0);
  const [roles, setRoles] = useState<{ name: string; count: number | null }[]>(
    [],
  );
  const [online, setOnline] = useState(true);

  useEffect(() => {
    async function load() {
      const filters = await get<Filters>("/api/filters");
      const first = await get<Page>("/api/listings?per_page=1");
      setOnline(Boolean(filters) && Boolean(first));
      if (first) setListings(first.total);
      if (!filters) return;
      setTracked(trackedTotal(filters.status_counts));
      setRoles(filters.roles.map((name) => ({ name, count: null })));
      const counted = await Promise.all(
        filters.roles.map(async (name) => {
          const page = await get<Page>(
            `/api/listings?per_page=1&role=${encodeURIComponent(name)}`,
          );
          return { name, count: page ? page.total : null };
        }),
      );
      setRoles(counted);
    }
    load();
  }, []);

  return (
    <div className="relative flex h-screen min-h-0">
      <Sidebar
        listings={listings}
        tracked={tracked}
        roles={roles}
        online={online}
      />

      <main className="relative flex h-full min-h-0 min-w-0 flex-1 flex-col">
        <div className="glow pointer-events-none absolute inset-x-0 top-0 h-[300px]" />

        <header className="relative px-8 pt-[30px]">
          <div className="flex items-baseline gap-3">
            <h1 className="m-0 text-[28px] leading-[1.1] font-semibold tracking-[-0.022em]">
              {title}
            </h1>
            <span className="font-mono text-[12px] text-text-4">{today()}</span>
          </div>
        </header>

        {toolbar}

        <div
          className="relative min-h-0 flex-1 overflow-auto px-8 pb-10"
          style={{ paddingTop: tight ? 4 : 22 }}
        >
          {children}
        </div>
      </main>

      <div
        className="relative z-3 h-full shrink-0 overflow-hidden border-l bg-surface transition-[width] duration-[var(--duration-standard)] ease-panel"
        style={{
          width: panel ? 420 : 0,
          borderColor: panel ? "rgba(0,0,0,0.08)" : "transparent",
        }}
      >
        {panel}
      </div>
    </div>
  );
}
