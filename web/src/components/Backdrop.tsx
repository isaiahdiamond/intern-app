import { useState } from "react";
import type { Background } from "@/lib/backgrounds";

export default function Backdrop({ image }: { image: Background }) {
  const [loaded, setLoaded] = useState(false);

  return (
    <div className="backdrop" aria-hidden="true">
      <div
        className="backdrop-fallback"
        style={{ background: image.fallback }}
      />
      <img
        className="backdrop-img"
        data-loaded={loaded}
        src={image.src}
        alt=""
        loading="eager"
        decoding="async"
        fetchPriority="high"
        onLoad={() => setLoaded(true)}
      />
      <div className="backdrop-scrim" />
    </div>
  );
}
