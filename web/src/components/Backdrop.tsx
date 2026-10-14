import { useState } from "react";
import { slots } from "@/lib/slots";
import type { Slot } from "@/lib/slots";

export default function Backdrop({
  slot,
  full,
}: {
  slot: Slot;
  full?: boolean;
}) {
  const [loaded, setLoaded] = useState(false);
  const image = slots[slot];
  return (
    <div
      className={full ? "backdrop backdrop-full" : "backdrop"}
      aria-hidden="true"
    >
      <div
        className="backdrop-fallback"
        style={{ background: image.fallback }}
      />
      {image.src ? (
        <img
          className="backdrop-img"
          data-loaded={loaded}
          src={image.src}
          alt=""
          loading="eager"
          decoding="async"
          onLoad={() => setLoaded(true)}
        />
      ) : null}
      <div className="backdrop-scrim" />
    </div>
  );
}
