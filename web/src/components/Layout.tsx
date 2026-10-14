import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import type { Filters } from "@/lib/api";
import { get, today } from "@/lib/api";
import { slots } from "@/lib/slots";
import type { Slot } from "@/lib/slots";
import Backdrop from "./Backdrop";
import Rail from "./Rail";

export default function Layout({
  title,
  subtitle,
  slot,
  actions,
  panel,
  children,
}: {
  title: string;
  subtitle?: string;
  slot: Slot;
  actions?: ReactNode;
  panel?: ReactNode;
  children: ReactNode;
}) {
  const [online, setOnline] = useState(true);

  useEffect(() => {
    async function load() {
      setOnline(Boolean(await get<Filters>("/api/filters")));
    }
    load();
  }, []);

  // White titles belong on a photograph. The seven gradient slots are pale, so
  // their titles stay on ink and keep their contrast.
  const onPhoto = slots[slot].src !== "";

  return (
    <>
      <Rail online={online} />
      <Backdrop slot={slot} />
      <div className="page">
        <main className="page-main">
          <div className="page-inner">
            <header className="mb-8 flex items-end gap-4">
              <div className="min-w-0">
                <h1
                  className="m-0 text-title"
                  style={{
                    color: onPhoto
                      ? "var(--color-ink-inverse)"
                      : "var(--color-ink)",
                  }}
                >
                  {title}
                </h1>
                <p
                  className="mt-2 mb-0 text-lead"
                  style={{
                    color: onPhoto
                      ? "rgba(255,255,255,0.88)"
                      : "var(--color-ink-3)",
                  }}
                >
                  {subtitle ?? today()}
                </p>
              </div>
              {actions ? (
                <div className="ml-auto flex shrink-0 items-center gap-2">
                  {actions}
                </div>
              ) : null}
            </header>
            {children}
          </div>
        </main>

        <div
          className="page-panel shrink-0"
          style={{
            width: panel ? "var(--panel-w)" : 0,
            borderLeft: panel ? "1px solid var(--color-line)" : "none",
            boxShadow: panel ? "var(--shadow-panel)" : "none",
          }}
        >
          {panel}
        </div>
      </div>
    </>
  );
}
