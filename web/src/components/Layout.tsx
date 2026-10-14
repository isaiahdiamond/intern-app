import type { ReactNode } from "react";
import { useOutletContext } from "react-router-dom";
import { today } from "@/lib/api";
import type { ShellContext } from "./Shell";
import ProfileMenu from "./ProfileMenu";

export default function Layout({
  title,
  subtitle,
  narrow,
  actions,
  panel,
  children,
}: {
  title: string;
  subtitle?: string;
  narrow?: boolean;
  actions?: ReactNode;
  panel?: ReactNode;
  children: ReactNode;
}) {
  const { name } = useOutletContext<ShellContext>();

  return (
    <div className="page">
      <main className="page-main">
        <div className={narrow ? "page-inner page-narrow" : "page-inner"}>
          <header className="mb-[var(--gutter)]">
            <div className="mb-6 flex justify-end">
              <ProfileMenu name={name} />
            </div>
            <div className="flex items-end gap-6">
              <div className="min-w-0">
                <h1
                  className="m-0 text-title"
                  style={{ color: "var(--title-ink)" }}
                >
                  {title}
                </h1>
                <p
                  className="mt-2 mb-0 text-lead"
                  style={{ color: "var(--title-ink-2)" }}
                >
                  {subtitle ?? today()}
                </p>
              </div>
              {actions ? (
                <div className="ml-auto flex shrink-0 items-center gap-3">
                  {actions}
                </div>
              ) : null}
            </div>
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
  );
}
