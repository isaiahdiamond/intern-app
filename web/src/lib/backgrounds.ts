// The nine themes Settings offers. Each is a pair: the page backdrop and the
// hero card's companion — the same place seen closer, never the same frame
// cropped. Choosing a theme swaps both.
//
// `tone` says which ink a page title takes over the backdrop: light means the
// photograph is bright and the title is --color-ink, dark means the title is
// white. `heroRatio` is the measured worst-case contrast for white text across
// the hero image's bottom 45%, copied from the manifest, never guessed. Both
// sets of measurements are recorded in DESIGN.md §3.2.
//
// Each fallback gradient is sampled from its own image, so the instant before
// the photograph decodes already carries its colours.

export type Background = {
  key: string;
  label: string;
  tone: "light" | "dark";
  src: string;
  fallback: string;
  hero: string;
  heroRatio: number;
};

// The hero card is designed dark, so its fallback is a dark card and the white
// text on it does not move when the image is missing or slow.
export const heroFallback =
  "linear-gradient(145deg, #2E2E2E 0%, #171717 55%, #000000 100%)";

// DESIGN.md §3 sets 7:1 for white on the hero card. --scrim-image-card is on it
// always; a companion that measures under this gets a second wash on top rather
// than being shipped on the scrim's word alone.
export const heroFloor = 7;

export const backgrounds: Background[] = [
  {
    key: "meadow",
    label: "Meadow",
    tone: "light",
    src: "/img/bg/meadow.jpg",
    fallback: "linear-gradient(180deg, #D9DEE5 0%, #959B9E 50%, #787851 100%)",
    hero: "/img/hero/meadow.jpg",
    heroRatio: 18.6,
  },
  {
    key: "coast",
    label: "Coast",
    tone: "light",
    src: "/img/bg/coast.jpg",
    fallback: "linear-gradient(180deg, #B7B7BB 0%, #86888F 50%, #5C6973 100%)",
    hero: "/img/hero/coast.jpg",
    heroRatio: 10.9,
  },
  {
    key: "dunes",
    label: "Dunes",
    tone: "light",
    src: "/img/bg/dunes.jpg",
    fallback: "linear-gradient(180deg, #CECBC2 0%, #97643B 50%, #603F2A 100%)",
    hero: "/img/hero/dunes.jpg",
    heroRatio: 19.7,
  },
  {
    key: "alpine",
    label: "Alpine",
    tone: "light",
    src: "/img/bg/alpine.jpg",
    fallback: "linear-gradient(180deg, #ACC2DB 0%, #32557C 50%, #6285AD 100%)",
    hero: "/img/hero/alpine.jpg",
    heroRatio: 16.9,
  },
  {
    key: "forest",
    label: "Forest",
    tone: "light",
    src: "/img/bg/forest.jpg",
    fallback: "linear-gradient(180deg, #C4CDC9 0%, #8A9E98 50%, #3C5644 100%)",
    hero: "/img/hero/forest.jpg",
    heroRatio: 11.1,
  },
  {
    key: "clouds",
    label: "Clouds",
    tone: "light",
    src: "/img/bg/clouds.jpg",
    fallback: "linear-gradient(180deg, #B2B7D6 0%, #CEA6A2 50%, #8D7FA2 100%)",
    hero: "/img/hero/clouds.jpg",
    heroRatio: 12.0,
  },
  {
    key: "snow",
    label: "Snow",
    tone: "light",
    src: "/img/bg/snow.jpg",
    fallback: "linear-gradient(180deg, #E8EFF7 0%, #E3EBF3 50%, #E4ECF5 100%)",
    hero: "/img/hero/snow.jpg",
    heroRatio: 16.2,
  },
  {
    key: "dusk",
    label: "Dusk",
    tone: "dark",
    src: "/img/bg/dusk.jpg",
    fallback: "linear-gradient(180deg, #294578 0%, #031D35 50%, #010F0C 100%)",
    hero: "/img/hero/dusk.jpg",
    heroRatio: 18.9,
  },
  {
    key: "silk",
    label: "Silk",
    tone: "dark",
    src: "/img/bg/silk.jpg",
    fallback: "linear-gradient(180deg, #0B2216 0%, #0A1B11 50%, #07160E 100%)",
    hero: "/img/hero/silk.jpg",
    heroRatio: 20.1,
  },
];

export const defaultBackground = "meadow";

export function background(key: string) {
  return (
    backgrounds.find((item) => item.key === key) ??
    backgrounds.find((item) => item.key === defaultBackground) ??
    backgrounds[0]
  );
}
