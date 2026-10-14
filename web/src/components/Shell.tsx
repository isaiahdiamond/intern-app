import { useEffect, useRef, useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import type { Filters, Profile } from "@/lib/api";
import { get } from "@/lib/api";
import { background, defaultBackground } from "@/lib/backgrounds";
import Backdrop from "./Backdrop";
import Rail from "./Rail";

export type ShellContext = {
  chosen: string;
  choose: (key: string) => void;
  name: string;
  rename: (name: string) => void;
};

// The rail, the photograph and the connectivity check live here rather than in
// each page, so a route change swaps only the page's own content. Nothing in
// this component remounts between routes, which is what keeps the photograph
// from fading out and back every time.
export default function Shell() {
  const location = useLocation();
  const [online, setOnline] = useState(true);
  const [chosen, setChosen] = useState(defaultBackground);
  const [name, setName] = useState("");
  const picked = useRef(false);

  useEffect(() => {
    async function load() {
      const [filters, stored, profile] = await Promise.all([
        get<Filters>("/api/filters"),
        get<{ background: string }>("/api/settings"),
        get<Profile>("/api/profile"),
      ]);
      setOnline(Boolean(filters));
      if (profile?.profile) setName(profile.profile.name);
      // A background picked while this was in flight is the newer answer.
      if (stored && !picked.current) setChosen(stored.background);
    }
    load();
  }, []);

  function choose(key: string) {
    picked.current = true;
    setChosen(key);
  }

  const image = background(chosen);
  const onboarding = location.pathname === "/onboarding";

  return (
    <div className="shell" data-tone={image.tone}>
      <Backdrop image={image} />
      {onboarding ? null : <Rail online={online} />}
      <Outlet
        context={
          { chosen, choose, name, rename: setName } satisfies ShellContext
        }
      />
    </div>
  );
}
