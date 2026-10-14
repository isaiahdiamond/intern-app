# DESIGN.md

Source of truth for how intern-app looks and feels. Read this before creating or changing any file
under `web/`. Every value here is a token name plus its value. Don't invent a color, size, radius or
curve that isn't in this file. If something you need isn't covered, ask — the open questions at the
end of this document are the list of things that are genuinely undecided.

This replaces the previous Apple-desktop design language (light gray page, translucent blurred
sidebar, `#0A84FF` blue accent, 48px rows). The **Motion** section is carried forward from that
document essentially intact — it was written against the `better-ui` and `motion-design` skills and
still holds. Everything else is new. Each section ends with **Changed from** when it replaces
something that exists in `web/` today, so the implementation diff is predictable.

The visual reference is the Juney landing page; crops live in `design/references/juney/`. The
dashboard crop (`05-dashboard.jpg`) is the one to match: dark left icon rail, off-white page, white
cards, a KPI row with delta chips and sparklines, a right-hand activity rail, and one full-bleed
image card. We are copying its structure and density, not its green.

---

## 1. Principles

**One user, every day.** This app is run locally by one person who looks at it daily. It is a
scanning tool before it is anything else. Nothing decorative may cost a row of data or a moment of
legibility.

**Dense where you work, roomy where you decide.** Tables are dense. The detail panel, onboarding and
the profile are roomy.

**Why a scanning tool gets a photographic backdrop.** Because it is one person's tool, not a product
surface. A board of 4,083 identical gray rows is a chore to open; a room with a photograph in it is
not. The photograph exists to make the app worth returning to, and it is allowed only on the terms
below, which are not negotiable.

**The discipline that keeps it readable — read this twice:**

1. **The photograph is a page-level backdrop. It is never a surface.** It sits behind the whole app
   at `z-index: 0`, fixed and lightly blurred, scrimmed only when its tone calls for it. It does not
   move, parallax, loop or animate beyond a single fade-in on first paint — and because it is mounted
   once for the whole app rather than per page, that fade happens once per session, not once per
   route.
2. **Everything readable rides on a near-opaque surface above it.** Cards, rows, the toolbar, the
   detail panel, menus. No body text, table row, table header, form label, input, chip or helper
   line ever sits directly on a photograph.
3. **There is exactly one exception and it is specified by name:** the hero image card (§7.11), which
   is a full-bleed photograph carrying one large number and one label in white, over a mandated dark
   scrim, at a mandated minimum size. Category-tile titles (§7.12) follow the same rule. Nothing else
   may put text on an image, ever.
4. **Contrast is checked against the worst case, not the happy case** — see §2.5.
5. **If the image is missing, the page is still correct.** Every image slot has a CSS gradient
   fallback that renders when no asset exists. The layout is built and reviewed against the
   fallbacks first.

**Off-black is the accent.** `--color-ink` `#171717` fills primary buttons and marks the active nav.
`--color-accent` `#FF4E02` is rationed: at most one accent element per screen, reserved for a number
that should pull the eye (the "1,617 new" count). Orange used twice on a screen is orange used
wrongly.

**Status color is information.** Applied / interviewing / offer / rejected keep their existing hues
and meanings. People read those as state. Never restyle them for looks, never reuse their hues for
anything that is not a status.

**No invented data.** If the API doesn't have salary, logos, deadlines or skill matches, the UI says
so plainly rather than filling the space.

---

## 2. Color

All tokens are `@theme` entries in `web/src/index.css`, so Tailwind generates `bg-*`, `text-*` and
`border-*` utilities from them. Never write a raw hex or `rgba()` in a component.

### 2.1 Surfaces

| token                  | value                    | use                                                                                                                                                                                                                           |
| ---------------------- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--color-page`         | `#FAFAFA`                | the page background, and the base color under every backdrop and scrim                                                                                                                                                        |
| `--color-surface`      | `#FFFFFF`                | cards, rows, the toolbar, the detail panel, menus — opaque, on pages with no backdrop                                                                                                                                         |
| `--color-surface-veil` | `rgba(255,255,255,0.94)` | the same surfaces on a page that has a backdrop. 0.94 is the floor; never lower it. The page carries no scrim under a light background (§3.1), so the card is the only thing standing between a photograph and a line of text |
| `--color-surface-sunk` | `#F4F4F4`                | table headers, group headers, the inside of an inset search field                                                                                                                                                             |
| `--color-tile`         | `#EFEFEF`                | company icon tile, chart stubs, avatar fallbacks                                                                                                                                                                              |
| `--color-rail`         | `#171717`                | the dark left rail                                                                                                                                                                                                            |
| `--color-rail-hover`   | `rgba(255,255,255,0.06)` | rail icon hover                                                                                                                                                                                                               |
| `--color-rail-active`  | `rgba(255,255,255,0.10)` | rail icon active fill — 1.32:1 against the rail, deliberately subtle (§6.1)                                                                                                                                                   |
| `--color-rail-edge`    | `rgba(255,255,255,0.14)` | the floating rail's hairline outline — 1.52:1 against the rail                                                                                                                                                                |

Cards on a backdrop page use `--color-surface-veil` and **no `backdrop-filter`**. An earlier draft
put `blur(20px) saturate(1.05)` on every card, on the reasoning that the blur is what makes 0.94 read
as solid. That reasoning does not survive the measurement: the backdrop image is already blurred
(§3.1), so the 6% of it that comes through a card is smooth before the card touches it, and a
per-card `backdrop-filter` re-blurs smooth pixels while costing one composited layer per card on a
page that now carries a dozen of them over a full-bleed photograph.

Measured on the live page, the worst pixel of a card over the darkest shipped background (`dusk`,
`silk`) composites to **#F0F0F0**, and over the brightest (`snow`) to **#FCFDFE**. Against #F0F0F0:
`--color-ink` 15.7:1, `--color-ink-2` 11.3:1, `--color-ink-3` 5.0:1, `--color-accent-ink` 5.2:1 —
every tier clears its floor, so 0.94 stays and the blur goes. The card's separation from a bright
photograph comes from `--color-line-strong` plus `--shadow-card` instead (§5.3).

### 2.2 Ink

| token                 | value     | contrast on `#FFFFFF` | use                                                                                                                                  |
| --------------------- | --------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `--color-ink`         | `#171717` | 16.0:1                | titles, row primary text, numbers, primary button fill                                                                               |
| `--color-ink-2`       | `#323232` | 11.9:1                | body copy, secondary row text, table values                                                                                          |
| `--color-ink-3`       | `#666666` | 5.7:1                 | labels, meta, timestamps, column headers, placeholders. **The lowest tier allowed for any text anywhere, including over a backdrop** |
| `--color-ink-4`       | `#8A8A8A` | 3.5:1                 | **never informational text.** Disabled labels, inactive rail icons, decorative glyphs, chart gridlines                               |
| `--color-ink-inverse` | `#FFFFFF` | —                     | text on `--color-ink` and on the hero image card                                                                                     |

### 2.3 Lines

| token                 | value                 | use                                                                        |
| --------------------- | --------------------- | -------------------------------------------------------------------------- |
| `--color-line`        | `rgba(23,23,23,0.08)` | card borders, control borders                                              |
| `--color-line-soft`   | `rgba(23,23,23,0.06)` | dividers inside a card, between table rows                                 |
| `--color-line-strong` | `rgba(23,23,23,0.14)` | input borders, menu borders, outline buttons. Meets the 3:1 non-text floor |

### 2.4 Accent and state fills

| token                 | value                 | use                                                                                                                                  |
| --------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `--color-accent`      | `#FF4E02`             | the one hot number per screen; the unread dot. **Never a background for text smaller than 24px, and never a text color at any size** |
| `--color-accent-ink`  | `#B83300`             | when accent must be _text_ — 6.0:1 on white, 5.0:1 on the worst-case card                                                            |
| `--color-accent-soft` | `rgba(255,78,2,0.10)` | the tint behind an accent number                                                                                                     |
| `--color-hover`       | `rgba(23,23,23,0.04)` | control and menu-item hover                                                                                                          |
| `--color-row-hover`   | `rgba(23,23,23,0.03)` | table row hover                                                                                                                      |
| `--color-selected`    | `rgba(23,23,23,0.06)` | the selected row, with a 2px `--color-ink` left marker                                                                               |
| `--color-track`       | `rgba(23,23,23,0.06)` | segmented-control track, secondary button fill                                                                                       |
| `--color-ring`        | `rgba(23,23,23,0.28)` | focus ring                                                                                                                           |
| `--color-chart-dot`   | `rgba(23,23,23,0.16)` | the activity chart's empty-day dot (§7.15). Non-text, so the 3:1 floor does not apply; it is a mark on the axis, not information read as a value |

`#FF4E02` is 3.3:1 on white. That clears the 3:1 large-text floor at 24px/600 and above, and nothing
else. This is why the accent is a number token and not a button color.

### 2.5 The contrast floor, and how to check it

**Floor:** 4.5:1 for all text below 24px (or below 18.66px bold); 3:1 for text at 24px/600 and above
and for the boundary of any input, checkbox or control the user must find. Disabled text is exempt,
which is the only reason `--color-ink-4` exists.

**Check against the worst case, not against white.** A card is `rgba(255,255,255,0.94)` over an
unknown photograph. The darkest that composite can be is white at 0.94 over pure black:

```
0.94 × 255 = 239.7  →  #EFEFEF
```

Measured on the approved backdrop the card lands at 17.1:1 for `--color-ink`, well inside this. The
table below keeps the pure-black worst case anyway, because the next backdrop may be brighter.

So **every text color is measured against `#EFEFEF`, not `#FFFFFF`.** Results:

| color                          | on `#EFEFEF` | verdict                                                             |
| ------------------------------ | ------------ | ------------------------------------------------------------------- |
| `--color-ink` `#171717`        | 14.9:1       | pass                                                                |
| `--color-ink-2` `#323232`      | 10.7:1       | pass                                                                |
| `--color-ink-3` `#666666`      | 4.8:1        | pass, with no margin — do not darken the page or lighten this token |
| `--color-ink-4` `#8A8A8A`      | 2.9:1        | fails; non-text only, as stated                                     |
| `--color-accent-ink` `#B83300` | 5.0:1        | pass                                                                |

**Text directly on the backdrop — the title's ink follows the background's tone.** Page titles, the
date or subtitle beneath them, and the "Jobs by Adzuna" line sit on the photograph, not on a card.
Which ink they take is **not a judgement and not a constant**: every shipped background declares a
`tone`, and the tone decides.

| tone                               | title                           | subtitle and the Adzuna line | page scrim         |
| ---------------------------------- | ------------------------------- | ---------------------------- | ------------------ |
| `light` — the photograph is bright | `--color-ink` `#171717`         | `--color-ink-2` `#323232`    | none               |
| `dark` — the photograph is deep    | `--color-ink-inverse` `#FFFFFF` | `rgba(255,255,255,0.86)`     | `rgba(0,0,0,0.18)` |

This inverts the previous rule, which made every backdrop title white. That rule was written when the
only backdrop was a near-black abstract; seven of the nine shipped photographs are bright, and white
on them is unreadable. The tone is carried on the shell element as `data-tone`, which redefines
`--title-ink`, `--title-ink-2` and `--scrim-page` for everything beneath it. **Nothing drives the
title colour off a guess, off the page, or off the file name** — only off `tone`.

The per-background measurements are the table in §3.2. The rules that follow:

- A new background is not shipped until its worst-case title contrast has been measured in the title
  zone at the shipped blur, with its tone's scrim applied, and clears **4.5:1 at every size** — not
  only the 3:1 large-text floor the 32px title would be entitled to.
- `tone` is a measured property of the asset, written into `web/public/img/bg/manifest.json` and
  mirrored in `web/src/lib/backgrounds.ts`. Changing an image means re-measuring and possibly
  re-tagging its tone.
- No body text, table row, form label or control ever sits on the backdrop. Those live on cards.
  The backdrop carries the page title, its subtitle and the attribution line, and nothing else.

On a page with no backdrop, titles are `--color-ink` as usual.

**How to verify a screen:** open devtools, set the backdrop `<img>` to `background: #000` with
`opacity: 1` and no scrim, then run the contrast checker on every text node on the page. If anything
below 24px reads under 4.5:1 in that state, it is a bug — not a lighting problem to be solved by
choosing a brighter photograph. Do this once per new screen and once per new image slot.

### 2.6 Status palette

Unchanged hues and meanings. These are the backend's keys, which is what `POST /api/status` accepts.

| key            | label        | text      | background              | dot       |
| -------------- | ------------ | --------- | ----------------------- | --------- |
| `new`          | New          | `#171717` | `rgba(23,23,23,0.07)`   | `#171717` |
| `saved`        | Saved        | `#9A5400` | `rgba(255,149,0,0.13)`  | `#FF9500` |
| `applied`      | Applied      | `#1E7A34` | `rgba(52,199,89,0.14)`  | `#34C759` |
| `interviewing` | Interviewing | `#7A3DA8` | `rgba(175,82,222,0.12)` | `#AF52DE` |
| `offer`        | Offer        | `#0B6E80` | `rgba(48,176,199,0.15)` | `#30B0C7` |
| `rejected`     | Rejected     | `#666666` | `rgba(23,23,23,0.05)`   | `#AEAEB2` |
| `hidden`       | Archived     | `#8A8A8A` | `rgba(23,23,23,0.04)`   | `#C7C7CC` |

`hidden` takes a listing off both the board and the tracker, so the status menu never offers it; it
is reached only through Archive, and exists in this table because a stored `hidden` row still turns
up in Search and must draw as something. A status key the table does not know draws gray and reads
"Unknown", never "New".

Backend connectivity dot: `--color-online` `#1E7A34`, `--color-offline` `#B3261E`. Both are the text
weight of their hue, because the dot sits on the dark rail where a bright `#34C759` glares.

**Changed from:** `new` was `#0066CC` blue and `rejected`/`hidden` used `#6E6E73`/`#8E8E93`. Blue has
left the palette entirely, so `new` is now the neutral ink pill; the accent is reserved for the
_count_ of new listings, not for the per-row pill. Online/offline dots were `#34C759`/`#FF3B30`.

### 2.7 Deleted tokens

Every `--color-accent*` blue (`#0A84FF`, `#0077ED`, `#0066CC`), `--color-bg` `#F5F5F7`,
`--color-sidebar` and the `.sidebar-blur` and `.glow` component classes. Nothing may reference them
after the implementation task.

---

## 3. Imagery

### 3.1 How a backdrop is built

There is **one backdrop, not one per page**. It is a photograph chosen in Profile & settings, stored
by the API as the `background` setting, and rendered behind every screen including onboarding. Slots
per page are gone: a page no longer picks its own image.

The backdrop is mounted once, in `Shell`, above the router outlet. It does not remount on a route
change, so it never fades out and back when you move between pages.

```
<div class="shell" data-tone="light|dark">
  <div class="backdrop" aria-hidden="true">     /* fixed, inset 0, z-index 0 — full bleed */
    <div class="backdrop-fallback"></div>       /* the image's own gradient, always present */
    <img class="backdrop-img" ... />            /* the photograph */
    <div class="backdrop-scrim"></div>          /* --scrim-page, which the tone sets */
  </div>
  <aside class="rail">…</aside>                 /* floats over the photograph (§6.1) */
  <div class="page">…</div>                     /* z-index 1 */
</div>
```

| layer                | treatment                                                                                                                                     |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `.backdrop`          | `position: fixed; inset: 0; z-index: 0; overflow: hidden; pointer-events: none`. Full bleed — the photograph runs under the rail's gutter too |
| `.backdrop-fallback` | the chosen image's own gradient, `position: absolute; inset: 0`                                                                               |
| `.backdrop-img`      | `width/height: 100%; object-fit: cover; filter: saturate(0.92) blur(3px); transform: scale(1.03)`. Fades in once on `load` (§9)               |
| `.backdrop-scrim`    | `background: var(--scrim-page)` — transparent under a light tone, `rgba(0,0,0,0.18)` under a dark one                                         |

**Why the blur is 3px and not 10px.** The old value was tuned to stop a dark abstract competing with
the content. A photograph at 10px is mush: the user asked for a photograph and would have got a wash.
At 3px it still reads as a backdrop rather than a wallpaper, and the worst-case title contrast moves
by at most 1.2 points, which the margins absorb (§3.2). The blur is on the image, not a
`backdrop-filter`, because it must composite once rather than on every scroll frame.

**Why the light tone has no scrim.** Measured in the title zone at the shipped blur, the old
`rgba(250,250,250,0.12→0.20)` scrim bought `--color-ink` about one point of contrast it did not need
(worst case 7.3:1 without it) while visibly flattening the photograph — and on the two dark
backgrounds it _removed_ contrast, taking white title text on `dusk` from 9.2:1 to 6.0:1, and to
4.2:1 at a slightly heavier mix. A scrim tuned for a dark image is the wrong scrim for a bright one.
So the light tone ships bare and the dark tone gets a gentle `rgba(0,0,0,0.18)`, which raises `dusk`
to 11.3:1 and `silk` to 15.6:1.

**Scrim and backdrop tokens**

| token                | value                                                                                    |
| -------------------- | ---------------------------------------------------------------------------------------- |
| `--scrim-page`       | `transparent` (light tone)                                                               |
| `--scrim-page-dark`  | `rgba(0,0,0,0.18)` — what `data-tone="dark"` assigns to `--scrim-page`                   |
| `--scrim-image-card` | `linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.25) 45%, rgba(0,0,0,0.62) 100%)` |
| `--backdrop-filter`  | `saturate(0.92) blur(3px)`                                                               |
| `--backdrop-scale`   | `1.03`                                                                                   |

**Asset rules:** JPEG, sRGB, `loading="eager"`, `decoding="async"`, `fetchPriority="high"`, under
400 KB after export, stored in `web/public/img/bg/`, filename equal to the key. Every backdrop
`<img>` carries `alt=""` and its wrapper `aria-hidden="true"`.

**The fallback is the image's own colours.** Each background's gradient is sampled from three bands
of its own file, so the instant before the photograph decodes is already in the right key rather than
a generic off-white. The layout must still be correct on the gradient alone — that is what renders
with `prefers-reduced-transparency: reduce`, which drops the image entirely.

### 3.2 The nine backgrounds

All nine ship. They are listed in `web/public/img/bg/manifest.json` and in
`web/src/lib/backgrounds.ts`; the two must agree. `meadow` is the default.

`ratio` below is the **worst pixel** of the title zone, measured on the rendered page at the shipped
blur and scale, with the tone's scrim applied, against the ink that tone assigns. The floor is 4.5:1.
The subtitle column is the same measurement against `--color-ink-2` / `rgba(255,255,255,0.86)`.

| key      | label  | tone  | title ink             | title  | subtitle |
| -------- | ------ | ----- | --------------------- | ------ | -------- |
| `meadow` | Meadow | light | `--color-ink`         | 14.6:1 | 10.8:1   |
| `coast`  | Coast  | light | `--color-ink`         | 10.8:1 | 7.7:1    |
| `dunes`  | Dunes  | light | `--color-ink`         | 9.4:1  | 7.1:1    |
| `alpine` | Alpine | light | `--color-ink`         | 7.7:1  | 5.7:1    |
| `forest` | Forest | light | `--color-ink`         | 12.3:1 | 7.7:1    |
| `clouds` | Clouds | light | `--color-ink`         | 8.2:1  | 6.3:1    |
| `snow`   | Snow   | light | `--color-ink`         | 15.3:1 | 11.1:1   |
| `dusk`   | Dusk   | dark  | `--color-ink-inverse` | 13.4:1 | 13.1:1   |
| `silk`   | Silk   | dark  | `--color-ink-inverse` | 16:1   | 16.6:1   |

`alpine` is the tightest at 7.7:1 for the title and 5.7:1 for the subtitle, and it is still comfortably
over the floor. Nothing in this table was taken from the mean luminance of the frame: every number is
the worst pixel under the text's own box.

**The hero companions** — 3:2, `img/hero/<key>.jpg`, one per theme, the fifth cell of the KPI row and
the only place text sits on a photograph (§7.11). Each carries a harder requirement than its
backdrop:

- **White on the scrimmed lower third must measure ≥ 7:1**, and the number is the _measured_ one from
  the manifest's `hero` entry, mirrored into `heroRatio` in `backgrounds.ts`. A hero asset chosen by
  eye once measured 1.6:1 and looked fine. Measure, do not look.
- Every companion is directed into deep shadow across its bottom 45%, which is where the number and
  the label sit.
- **`--scrim-image-card` stays on the card regardless.** The dark base is the belt, the scrim is the
  braces, and neither is allowed to be doing the job alone.
- A companion whose measured ratio lands below `heroFloor` 7 gets a second `rgba(0,0,0,0.28)` wash
  across the card's lower half. That adjustment is driven off the measured number, never off which
  image it is.
- _Fallback:_ `linear-gradient(145deg, #2E2E2E 0%, #171717 55%, #000000 100%)`, shared by all nine.
  The card is designed dark, so a missing or slow companion leaves the text exactly where it was.

**The remaining content image:**

**`profile-cover`** — 4:1, a banner across the top of the profile card, with the avatar and name
_below_ it on the card, never on the image. Runs on its gradient:
`linear-gradient(90deg, #F0EDE9 0%, #F6F6F6 50%, #EFF1F3 100%)`, with `inset 0 -1px 0
var(--color-line)` at its bottom edge.

**Deleted.** The six per-page `backdrop-*` slots and `coach-empty` are gone, with
`web/src/lib/slots.ts`, and the single `hero-card-dashboard.jpg` is replaced by the per-theme
companions. A page does not choose an image; the theme does, and it chooses both at once.

### 3.3 Image outlines

Every content image — `profile-cover`, the hero card, a background thumbnail in the picker — takes
rgba(0,0,0,0.1); outline-offset: -1px`, per `better-ui`. Never a palette near-black and never the
accent: a tinted outline shows as a colored fringe. Backdrops are exempt; they have no visible edge.

### 3.4 Things imagery may never do

No image behind a table body, a form or the detail panel's content. No image in a row, a pill, a
chip, a menu or a button. No company logos (see §5.2 — the privacy reason is unchanged). No parallax,
no Ken Burns, no video, no loop. No image slot that isn't in §3.2. No per-page backdrop: there is one background and the setting
chooses it.

---

## 4. Type

Fonts are unchanged; the scale is not.

```
--font-sans:    -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display",
                "Helvetica Neue", system-ui, sans-serif
--font-display: -apple-system, BlinkMacSystemFont, "SF Pro Display", system-ui, sans-serif
--font-mono:    ui-monospace, "SF Mono", Menlo, monospace
```

Body default is **14px / 1.45 / `-0.006em`** on `--color-ink-2`.

| token             | size | line | weight | tracking               | use                                               |
| ----------------- | ---- | ---- | ------ | ---------------------- | ------------------------------------------------- |
| `--text-display`  | 40px | 1.05 | 600    | -0.032em, tabular-nums | KPI numbers, the hero card number                 |
| `--text-title`    | 32px | 1.15 | 600    | -0.026em               | page titles                                       |
| `--text-title-lg` | 38px | 1.1  | 600    | -0.028em               | onboarding title only                             |
| `--text-section`  | 20px | 1.25 | 600    | -0.018em               | card titles, panel title, group headers           |
| `--text-lead`     | 16px | 1.5  | 400    | -0.01em                | page subtitle, panel body, empty-state sentence   |
| `--text-row`      | 15px | 1.35 | 500    | -0.008em               | row primary text (role, company). 600 when unread |
| `--text-body`     | 14px | 1.45 | 400    | -0.006em               | the default                                       |
| `--text-control`  | 14px | 1    | 500    | -0.004em               | buttons, filter chips, menu items, inputs         |
| `--text-meta`     | 13px | 1.3  | 500    | 0                      | location, timestamps, counts, secondary row line  |
| `--text-label`    | 12px | 1.2  | 600    | 0.04em, uppercase      | column headers, KPI card labels                   |
| `--text-tag`      | 12px | 1    | 500    | 0                      | title tags, delta chips (mono)                    |

Weight never exceeds 600. Uppercase only on `--text-label`. `font-variant-numeric: tabular-nums` on
every number that changes: KPI values, counts, delta chips, the hero number, row dates.

Mono (`--font-mono`) carries counts, dates, ids, title tags, URLs and the Adzuna attribution line.

**Changed from:** body 13px → 14px; page title 28px → 32px; stat number 34px → 40px; card title 15px
→ 20px; row text 13px → 15px; controls 12.5px → 14px; column headers 11px → 12px. Line height 1.35 →
1.45. This is the type half of the density change in §0 — the user accepts ~9 rows per screen where
there were ~14.

---

## 5. Space, radius, depth

### 5.1 Spacing

**`--gutter` 16px is the one number between containers.** Horizontal gaps between cards, vertical
gaps between rows, the gap between the rail and the content, and the page's top and side padding are
all exactly this, with no exceptions and no per-component judgement. Every value below is for space
_inside_ a container; the space _between_ containers is `--gutter` and only `--gutter`.

A uniform gutter is necessary and was not sufficient: the dashboard read as uneven at 24px even
though every gap already measured 24px, because the two columns drifted out of step. So the rule has
two halves and both are binding:

1. **One gutter, both axes** — `--gutter` 16px.
2. **Rows line up across columns** — §6.3.

Measured on the dashboard at 1440 after the change: content starts at x=102 with the rail's right
edge at 86 (a 16px gutter), y=16; every card gap is 16px; both columns start their second row at
y=816, a drift of 0px. Before: 24px gaps, content at x=140, and the two columns' second rows
starting 111px apart.

The rest is a 4px scale for space inside a container. Use the token, not the number.

| token        | value | typical use                                  |
| ------------ | ----- | -------------------------------------------- |
| `--space-1`  | 4px   | icon-to-label inside a pill                  |
| `--space-2`  | 8px   | tag gaps, chip internals                     |
| `--space-3`  | 12px  | control internals, row internal stacking     |
| `--space-4`  | 16px  | card padding (small), grid gap               |
| `--space-5`  | 20px  | —                                            |
| `--space-6`  | 24px  | card padding (default), gap between cards    |
| `--space-8`  | 32px  | page gutter, gap between card and table      |
| `--space-10` | 40px  | inside a roomy container                     |
| `--space-12` | 48px  | empty-state padding, bottom of a scroll area |
| `--space-16` | 64px  | onboarding block spacing                     |

| token      | value | use                                                                                                           |
| ---------- | ----- | ------------------------------------------------------------------------------------------------------------- |
| `--gutter` | 16px  | **between containers, and only between containers** — card to card, row to row, rail to content, page padding |

**Changed from:** card padding 20px → 24px. The page gutter and the between-card gap were 40px and
24px and are now both `--gutter` 16px. Card padding and row height did **not** change with it: this
was about the space between containers, not inside them, and 64px rows and the type scale are
untouched.

### 5.2 Radius

Measured off the crops. Juney's radii are generous and its controls are capsules.

| token           | value | use                                                                                      |
| --------------- | ----- | ---------------------------------------------------------------------------------------- |
| `--radius-xs`   | 6px   | title tags, checkboxes                                                                   |
| `--radius-sm`   | 8px   | company icon tile (small), delta chip                                                    |
| `--radius-md`   | 12px  | rail icon buttons, inputs, menu items, company tile (panel)                              |
| `--radius-lg`   | 16px  | menus, popovers, inner cards, the segmented track                                        |
| `--radius-xl`   | 20px  | KPI cards, the hero image card, the activity rail card                                   |
| `--radius-2xl`  | 28px  | the page's big container cards (table card, chart card), the detail panel                |
| `--radius-full` | 999px | every button, every filter chip, every status pill, every segment, every onboarding chip |

Apply `better-ui`'s concentric rule: where a card is padded and holds a nested surface, the outer
radius is the inner radius plus the padding. A `--radius-2xl` 28px card with `--space-3` 12px padding
holds a `--radius-lg` 16px inner surface. Past 24px of padding, treat the layers as separate and keep
each one's token.

**Changed from:** nearly everything. Controls were 8px and are now capsules; cards were 16px and are
now 20–28px; pills were 11–13px and are now `--radius-full`.

### 5.3 Shadows and borders

| token            | value                                                                  | use                                                                                                                   |
| ---------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `--shadow-card`  | `0 1px 2px rgba(23,23,23,0.04), 0 12px 32px -16px rgba(23,23,23,0.10)` | KPI cards, container cards, the hero image card                                                                       |
| `--shadow-float` | `0 16px 40px -8px rgba(23,23,23,0.16), 0 2px 6px rgba(23,23,23,0.06)`  | menus, popovers, the status menu                                                                                      |
| `--shadow-seg`   | `0 1px 2px rgba(23,23,23,0.10), 0 0 0 0.5px rgba(23,23,23,0.06)`       | the selected segment                                                                                                  |
| `--shadow-panel` | `-16px 0 48px -24px rgba(23,23,23,0.18)`                               | the detail panel's left edge                                                                                          |
| `--shadow-rail`  | `0 18px 44px -12px rgba(0,0,0,0.42), 0 2px 8px rgba(0,0,0,0.16)`       | the floating rail. Tuned to pure black, not `#171717`, because it falls on a photograph rather than on the page color |

Shadows carry elevation, borders carry structure (`better-ui`). Keep borders on dividers, table rows,
inputs and selected states; drop them where they only faked depth. Every element with a shadow ring
also carries `border: 1px solid transparent`, so forced-colors mode — which strips every `box-shadow`
— still draws an edge.

On a backdrop page, a card takes **both** `--shadow-card` and a 1px `--color-line-strong` border.
Over a photograph a shadow alone does not separate a surface from its background, and over a _bright_
photograph — `snow` sits at L 0.88 — the softer `--color-line` does not either. This is one of the
changes the brighter backdrops forced.

**Changed from:** `--shadow-card` and `--shadow-menu` were tuned to pure black; both are retuned to
`#171717` and made slightly deeper, because they now have to work over a photograph.
`--shadow-panel` is new, for the same reason.

---

## 6. Layout

```
--rail-w:      72px   the floating rail's own width
--rail-inset:  14px   its gap from the window's left, top and bottom edges
--rail-radius: 30px   its corner radius
--panel-w:   460px    the detail panel
--page-max:  1440px   content max-width inside the page shell
--row-h:     64px     a table row
--row-h-sm:  56px     a row inside the activity rail
--toolbar-h: 64px     the filter / search toolbar

--kpi-h:     132px    the KPI row's height — the four cards and the hero (§7.10, §7.11)
--plot-h:    214px    the activity chart's plot floor (§7.15)
--dot-day:    10px    an empty day's dot on the chart baseline (§7.15)
--dot-day-wide: 6px   the same dot past 30 days, where a column is narrower than 10px
--avatar-lap: -8px    the avatar stack's overlap (§7.15)
--donut:     112px    the status donut (§7.19)
--donut-ring: 15px    its ring thickness, so the hole is 82px (§7.19)
--legend-h:   36px    a legend row in the status card (§7.19)
```

**Card heights are tokens, not component literals.** A card is sized to its content plus its
padding, and a card that shares a grid row with another carries the same token so neither stretches
into dead space. Measured at 1440 after the compression: a KPI card is 235 × 132 with 22px below its
caption — 20px of which is its own `--space-5` padding — where it was 235 × 200 with 82px. The chart
and the status card are both 359 tall where both were 435.

### 6.1 The floating rail

The rail does not touch the window. It is inset `--rail-inset` 14px from the left, top and bottom
edges, `--rail-w` 72px wide, `--rail-radius` 30px, `--color-rail` `#171717`, `z-index: 30`, and it
floats over the photograph with `--shadow-rail`. The backdrop runs full-bleed underneath, so the
photograph is visible in the gutter on all four sides of it.

**The outline is load-bearing.** A 1px `--color-rail-edge` `rgba(255,255,255,0.14)` hairline — a
low-opacity white, never a grey — measures 1.52:1 against the rail's own fill and is what gives the
slab its edge where the photograph behind it is dark. Without it the rail dissolves into `dusk` and
`silk`. It doubles as the forced-colors border that §5.3 requires under every shadow.

Contents, top to bottom:

- **App mark** — 40px, `--radius-full`, white fill, the mono "i" in `--color-ink`. The one bright
  thing on the rail.
- **Nav** — four items: Dashboard, All listings, Tracker, Coach. 44px square, `--radius-md`, stacked
  with `--space-2`. Icons 20px, `currentColor`, stroke 1.5 inactive / 2.1 active.
- **Bottom** — the API connectivity dot alone: 8px, `--color-online` / `--color-offline`, with an
  `aria-label` naming the state in words. Profile and settings is reached from the header's profile
  menu (§7.17), which is on every page; putting a second entry down here would be two controls for
  one destination.

**States.**

| state    | treatment                                                                                       | measured                                                        |
| -------- | ----------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| inactive | glyph `rgba(255,255,255,0.45)`, no fill                                                         | glyph 4.2:1 against the rail                                    |
| hover    | `--color-rail-hover` `rgba(255,255,255,0.06)` fill, glyph `rgba(255,255,255,0.80)`              | —                                                               |
| active   | `--color-rail-active` `rgba(255,255,255,0.10)` rounded-square fill, glyph `#FFFFFF`, stroke 2.1 | fill 1.32:1 against the rail; glyph 13.5:1 against its own fill |

**The active state is deliberately subtle, and there is no marker bar.** The earlier 3px × 20px
white left-edge marker is removed. What carries the state is a fill barely above the rail's own
colour plus the icon going solid — which is three channels, not one: the fill, the glyph's own jump
from 45% to 100% white, and the heavier stroke. `aria-current="page"`, which `NavLink` sets, carries
it for assistive technology.

**Tooltips.** Hovering or keyboard-focusing a rail item pops a bubble beside it: `--color-ink` fill,
`--color-ink-inverse` text at `--text-control`, 32px tall, `--radius-md`, `--shadow-float`,
`left: calc(100% + 20px)`, vertically centred on the item, `z-index: 40`. It is pure CSS — no state,
no library — driven by `:hover` inside `@media (hover: hover)` and by `:focus-visible`, so keyboard
users get the labels the icons do not carry. It is `aria-hidden` and `pointer-events: none`: the
accessible name stays on the item's own `title` and `aria-label`, which every rail item still has.
Timing is in §9.

**Changed from:** the edge-to-edge rail. Gone with it: the "+" add button (Add a job lives on the
Tracker page, which is where it always posted to), the gear, and Profile as its own nav item. The
rail is four destinations and a status dot; everything about the person is in the header menu.

### 6.2 The page shell

```
body            height 100vh; overflow hidden; background var(--color-page)
.rail           fixed, 0 0 0 0, width var(--rail-w)
.backdrop       fixed, inset 0, z-index 0 — full bleed, under the rail   (§3.1)
.page           margin-left calc(var(--rail-inset) + var(--rail-w));
                position relative; z-index 1;
                height 100vh; display flex
.page-main      flex 1; min-width 0; overflow-y auto; overscroll-behavior contain
.page-inner     max-width var(--page-max); margin 0 auto;
                padding var(--gutter) var(--gutter) var(--space-8)
.page-narrow    max-width calc(var(--measure) + var(--gutter) * 2)  — form pages
.page-panel     width var(--panel-w) (0 when closed); overflow-y auto;
                overscroll-behavior contain
```

The page itself never scrolls; the main column and the panel scroll independently. Desktop first; no
breakpoints below 1280px are specified and none are needed.

**Page header** sits inside `.page-inner` and is one horizontal band, `--space-8` above the content:

**Row one — the profile band.** The profile menu (§7.17) alone, right-aligned, `--space-6` above the
title block. It is a 32px control and nothing else shares the row: no search, no notifications, no
upgrade. It is on every page and never moves, so it is the one fixed point in the header.

**Row two — the title band**, bottom-aligned:

- **Left:** the page title at `--text-title` in `--title-ink`, and a one-line subtitle beneath it at
  `--text-lead` in `--title-ink-2`. Both sit on the photograph, so both follow the tone (§2.5). On
  the dashboard the title is the greeting (§7.16) and the subtitle is "Here's an overview of the
  latest listings and your applications" — which is what the page holds and nothing more.
- **Right:** the page's own actions. On the dashboard that is the activity chart's range control
  (§7.15) — it drives a card below but it lives up here, because the range is a property of the
  screen rather than of one card. On the tracker it is "Add a job".

`--gutter` below the header.

**Full-width pages and column pages.** The dashboard, All listings and the tracker use the whole
content area. **Form-style pages use a centred column of `--measure` 760px** — Profile & settings
today — and the column holds the _header too_, so the title sits over its own content instead of
floating off to its left. It is `.page-narrow` on `.page-inner`, which is a max-width plus the
`margin: 0 auto` that `.page-inner` already has. Measured at 1440 the column runs x=383 to x=1143
with 297px either side; at 1024 it is 89px either side, and below that the auto margins collapse to
the page's `--gutter` padding rather than to zero.

### 6.3 Grids

**KPI row** (dashboard) — the Juney `05` structure exactly:

```
grid-template-columns: repeat(4, minmax(0, 1fr)) 320px;
gap: var(--gutter);
```

Four KPI cards, then the theme's hero companion as the fifth cell at a fixed 320px.

**Dashboard body** — one grid, not two stacked columns:

```
grid-template-columns: minmax(0, 1fr) 340px;
gap: var(--gutter);
```

**Cards are grid items, never children of a per-column flex stack.** Two flex columns side by side
let each column set its own rhythm, so a tall card on one side pushes everything below it out of
step with the other side — on the dashboard that was 111px of drift and it is the single thing that
made a uniform 24px gutter read as uneven. As grid items in shared rows, both columns start every
row at the same y. Cards in a row stretch to the row's height, so a short card gains space at its
bottom rather than leaving a visible hole above the next row; the activity chart's plot grows to
fill it (§7.15).

**Listings / Tracker** — one full-width `--radius-2xl` container card holding the toolbar, the header
row and the rows. No side rail.

### 6.4 The table row, at 64px

The row is a CSS grid, never a flex row, so columns line up across rows.

|         | panel closed                                           | panel open                                       |
| ------- | ------------------------------------------------------ | ------------------------------------------------ |
| columns | `minmax(220px,1.1fr) minmax(0,2.4fr) 120px 112px 44px` | `minmax(160px,1fr) minmax(0,1.6fr) 0 112px 44px` |
| height  | `--row-h` 64px                                         | 64px                                             |
| padding | `0 var(--space-4) 0 var(--space-6)`                    | same                                             |

Columns, left to right: **company** (icon tile + company over location), **role** (`display_title` +
title tags), **posted** (mono date, hidden when the panel is open), **status** (pill), **action**
(the row menu button, revealed on hover, always present in the DOM for keyboard users).

Rows are separated by a 1px `--color-line-soft` top border, not by gaps. The row's own background is
transparent; the container card supplies the surface.

Group headers (tracker) are 48px, `--color-surface-sunk`, `--text-label`, sticky to the top of the
scroll area.

**Changed from:** rows were 48px with `minmax(140px,1fr) minmax(0,2.2fr) 72px <action>` and no posted
column at this width. 48px → 64px is the density decision; the extra 16px is what pays for 15px row
text at 1.35 and a 36px icon tile.

### 6.5 The detail panel

460px (was 420px), a flex sibling of `.page-main` that animates its width over
`--duration-standard` with `--ease-panel`. `--color-surface` opaque — the panel is the one surface
that does **not** veil, because it carries the longest body text in the app. A 1px `--color-line`
left border plus `--shadow-panel`.

- Header 64px: position text in mono, then prev / next / close as 36px ghost buttons.
- Body: 48px company tile, title at `--text-section`, company at `--text-body`, then a primary
  "Open posting" and a secondary next-status button.
- Properties: a 120px label column in `--text-label`, a 16px icon, then the value in `--text-body`.
  Status and link are last.
- Everything in it comes from the row. There is no description or parsed-requirement data in the API
  yet, and the panel says so in a sentence rather than showing an empty section.

---

## 7. Components

Every component below is a plain function component. No classes, no custom hooks, no abstraction
layers (CLAUDE.md, Frontend code style).

### 7.1 Buttons

All `--radius-full`, `--text-control`, icon 16px at stroke 1.5, gap `--space-2`.

| variant                  | height  | fill                     | text                  | border                    | hover                 |
| ------------------------ | ------- | ------------------------ | --------------------- | ------------------------- | --------------------- |
| primary                  | 40px    | `--color-ink`            | `--color-ink-inverse` | transparent               | `#000000`             |
| secondary                | 40px    | `--color-track`          | `--color-ink`         | transparent               | `rgba(23,23,23,0.10)` |
| outline                  | 40px    | `--color-surface`        | `--color-ink`         | 1px `--color-line-strong` | `--color-hover`       |
| ghost                    | 36px    | none                     | `--color-ink-3`       | none                      | `--color-hover`       |
| icon                     | 36px sq | none                     | `--color-ink-3`       | none                      | `--color-hover`       |
| hero (on the image card) | 36px    | `rgba(255,255,255,0.94)` | `--color-ink`         | transparent               | `#FFFFFF`             |

Padding is `0 var(--space-4)`, reduced by 2px on the icon side (`better-ui`, optical alignment). One
primary per screen. A disabled button is `opacity: 0.45`, `cursor: not-allowed`, and never scales.

**Changed from:** 30px tall, 8px radius, blue primary. Now 40px, capsule, off-black.

### 7.2 Company icon tile

36px / `--radius-sm` in rows, 44px / `--radius-md` on the dashboard, 48px / `--radius-md` in the
panel. `--color-tile` background with a centered 🏢 glyph showing through whenever there is no icon.

The apply URL is a job board, not the company, so the domain is resolved separately and the icon is
cached server-side. The page loads it from our own origin at `/api/icon/{company}`: the browser must
never request an icon from a third party, because that would tell a logo service which companies are
on the board. `has_icon` on the row says whether one exists — only request an icon when it does, and
never render a broken image.

**Changed from:** 28 / 34 / 40px → 36 / 44 / 48px.

### 7.3 Title tags

`level`, `education`, `term`, `citizenship`, years of experience — in that order, omitted when empty.
The first three come from the title; the last two only from the posting body, so a listing whose full
text we never collected shows at most three and must still look right.

22px tall, `--radius-xs`, `rgba(23,23,23,0.04)` on a 1px `--color-line-soft` border, `--text-tag`
mono, padding `0 var(--space-2)`, gap `--space-2`.

`citizenship` reads "US citizens", "Clearance" or "No sponsorship"; years reads "2+ yrs". These are
knockout facts, which is why they are on the row and not only in the panel. Keep every label inside
15 characters: the tags share the role column with a truncating `display_title`, and a long tag eats
the title instead of wrapping.

**Changed from:** 18px / 5px radius / 10.5px → 22px / `--radius-xs` / 12px.

### 7.4 Status pill

28px tall, `--radius-full`, `--text-control`, padding `0 var(--space-3)`, an 8px dot then the label,
colors from §2.6. 124px fixed width in a table column so the column lines up; auto width in the
panel. A 14px chevron at the right when it opens a menu.

**Changed from:** 22px / radius 11px / 12px / 108px wide / 6px dot.

### 7.5 Filter chip

40px tall, `--radius-full`, `--color-surface` on 1px `--color-line-strong`. Label in 500, the chosen
value beside it in 400 at `--color-ink-3`, then a 14px chevron that rotates 180° when open.

- active: `--color-ink` fill, `--color-ink-inverse` text, no border
- disabled (a filter that can't apply in the current mode): `opacity: 0.45`, does not open

**Changed from:** 30px, 8px radius, blue-tinted active state. Active is now a solid off-black
capsule, which is the Juney treatment and reads at a glance in a toolbar of eight chips.

### 7.6 Segmented control (tracker)

`--color-track` track, 4px padding, `--radius-full`; segments 36px, `--radius-full`,
`--text-control`. Selected is `--color-surface` with `--shadow-seg`. The count beside each label is
mono `--text-tag` at `--color-ink-3`. Every segment carries a 1px border — transparent except on the
selected one, which takes `rgba(23,23,23,0.06)` — so selecting shifts nothing and forced-colors mode
can still tell them apart.

### 7.7 Menus (status, filter, row actions)

200px (status) / 260px (filter) wide, `--space-1` padding, `--radius-lg`, `--color-surface` opaque,
1px `--color-line-strong`, `--shadow-float`, `overscroll-behavior: contain`, entering with
`--animate-pop`.

Items 40px, `--radius-md`, `--text-control`, padding `0 var(--space-3)`, hover `--color-hover`.
Status items: dot, label, and an `--color-ink` check on the current one. Filter items: 16px checkbox,
label, mono count right-aligned. Clicking the page background closes the menu; the menu stops
propagation.

### 7.8 Inputs

40px tall, `--radius-full` for search, `--radius-md` for a multi-line or form field.
`--color-surface` on 1px `--color-line-strong` (which is the 3:1 boundary the search field needs),
`--text-control`, padding `0 var(--space-4)`. Search carries a 16px magnifier on the left and an
`--space-2` gap. Placeholder is `--color-ink-3` — not `--color-ink-4`, because a placeholder is read.

Inside a container card, an input uses `--color-surface-sunk` with a `--color-line` border instead,
so it recedes rather than stacking a second white on white.

### 7.9 Cards

| card                     | radius                              | padding                              | surface                         |
| ------------------------ | ----------------------------------- | ------------------------------------ | ------------------------------- |
| container (table, chart) | `--radius-2xl`                      | `--space-3` around the inner surface | veil + border + `--shadow-card` |
| KPI                      | `--radius-xl`                       | `--space-5`                          | veil + border + `--shadow-card` |
| activity rail            | `--radius-xl`                       | `--space-5`                          | veil + border + `--shadow-card` |
| hero image               | `--radius-xl`                       | `--space-5`                          | the photograph (§7.11)          |
| panel                    | `--radius-2xl` on its outer corners | —                                    | opaque                          |

"veil" means `--color-surface-veil` `rgba(255,255,255,0.94)` with a 1px `--color-line-strong` border
and `--shadow-card`. No `backdrop-filter` — see §2.1 for the measurement that removed it.

### 7.10 KPI card

`--radius-xl`, `--space-5` padding, `--shadow-card`, height `--kpi-h` 132px.

**The height is the content's, not a round number.** 20 + 15 (label) + 12 + 42 (value) + 4 + 17
(caption) + 20 = 130, and the token rounds that to 132 so a system font with slightly different
metrics has somewhere to go. An earlier draft left the cards at a 200px row set by the hero's own
minimum; 82px of each card — 41% of it — was empty below the caption, which is what a card sized to
a neighbour rather than to its content looks like.

1. Label at `--text-label`, `--color-ink-3`.
   `--space-3` below it, then `--space-1` between the value and the caption.
2. Value at `--text-display`, `--color-ink`, tabular-nums. **If and only if this is the screen's one
   hot number, it is `--color-accent` instead** — on the dashboard that is the new-listings count,
   and nowhere else.
3. A caption line at `--text-meta`, `--color-ink-3` ("39 invoices" in the reference; "of 4,083" here).
4. A delta chip top-right, 24px, `--radius-sm`, mono `--text-tag`, with an arrow glyph:
   - positive `rgba(52,199,89,0.14)` / `#1E7A34`
   - negative `rgba(179,38,30,0.10)` / `#B3261E`
   - flat `rgba(23,23,23,0.05)` / `--color-ink-3`
     The arrow is the static cue; the color is the reinforcement, never the only channel.
5. A 40px sparkline across the bottom: 1.5px stroke, `--color-ink-4`, no fill, no dots, no axis. It
   is a texture, not a chart — it carries no labels and is `aria-hidden`.

### 7.11 Hero image card

The fifth cell of the KPI row, 320px wide, `--radius-xl`, `--shadow-card`, slot
the current theme's companion (§3.2), `--scrim-image-card` as an `::after`, image outline per
§3.3.

Content, bottom-aligned, `--space-5` padding:

- the count at `--text-display` in `--color-ink-inverse`
- one label at `--text-lead`/500 at `rgba(255,255,255,0.80)`
- up to two `hero` buttons in a row with `--space-2`

**The hero is the fifth cell of the KPI row, so its height is `--kpi-h` and nothing else.** It is
320 × 132 today. Minimum rendered size 320 × 124: below that the text no longer clears the scrim's
dark zone, and the card must be replaced by an ordinary KPI card rather than shrunk.

A shorter card changes which part of the photograph sits under the text, so the white text was
re-measured at the new height rather than assumed. Worst pixel in the text's own box, with
`--scrim-image-card` applied, against `--color-ink-inverse`, per theme:

| height | meadow | coast | dunes | alpine | forest | clouds | snow | dusk | silk |
| ------ | ------ | ----- | ----- | ------ | ------ | ------ | ---- | ---- | ---- |
| 200px  | 17.8   | 10.3  | 20.1  | 18.1   | 12.2   | 14.8   | 19.0 | 20.3 | 20.9 |
| 132px  | 16.9   | 8.3   | 20.0  | 17.3   | 10.3   | 13.2   | 18.6 | 20.2 | 20.9 |
| 124px  | 16.7   | 8.0   | 20.0  | 17.1   | 10.0   | 12.9   | 18.4 | 20.1 | 20.9 |

`coast` is the floor case and holds 8.3:1 at 132px against the 7:1 requirement, so no theme needs
the `heroRatio < heroFloor` wash at this height. 124px is where the table stops because `coast`
still clears 7 there with a margin worth having; that is the stated minimum and not a target.
`heroRatio` in `backgrounds.ts` is unchanged — it measures the image's own bottom 45%, which is a
property of the asset and not of the card.

### 7.12 Category tile (optional, not on any current screen)

The `02-category-tiles.jpg` treatment: a full-bleed photo tile with a white title. If one is ever
built, it obeys exactly the hero card's rules — `--scrim-image-card`, title at `--text-section` or
larger, no body text, no meta, nothing below 20px. It is listed here so that nobody invents a looser
version of it later.

### 7.13 Activity rail

A `--radius-xl` card, 340px, holding `--row-h-sm` 56px rows: a 32px avatar or icon tile, a two-line
body (`--text-body` with the subject in 600, then `--text-meta` at `--color-ink-3`), separated by 1px
`--color-line-soft`. A "Latest updates" caption under the `--text-section` title. Scrolls
independently with `overscroll-behavior: contain`.

### 7.14 Onboarding role chips

44px tall, `--radius-full`, `--text-lead`/500, `--color-surface` on 1px `--color-line-strong`.
Selected is `--color-ink` fill with `--color-ink-inverse` text. `scale(0.96)` while pressed, gated
behind `motion-safe:` (§8). "Other" is a dashed-border chip that becomes an inline input with an
"Add" button.

### 7.15 Activity chart (dashboard)

Replaces the plain 28-day bar chart. Same number — applications sent per day — but each day carries
the companies applied to that day, from `GET /api/activity?days=N`.

A `--radius-2xl` card, `--space-6` padding. Header: "Applications sent" at `--text-section` with a
mono `--text-meta` count beneath it ("9 in the last 7 days"). Nothing else — the card has no control
of its own.

**Range control.** It lives in the page header (§6.2), not in this card: a 40px `--radius-full`
outline button, "Last 7 days" with a 14px chevron, opening a `--radius-lg` menu. **The options come
from the endpoint's own `ranges` array** (3 / 7 / 14 / 30 / 90 today), never from a list typed into
the component. Default 7. The chart is a plain function of `days` and the fetched data; the page
owns both.

**The plot** flexes to fill whatever height the grid row gives the card, with a `--plot-h` 214px
floor and a 1px `--color-line-soft` baseline. Bar heights are a percentage of it (the tallest takes
36%, leaving the rest for the avatar stack), so the chart grows into a stretched row instead of
leaving dead space under itself. The floor and the share are set together: they are what has to
hold a stack of six 24px avatars at `--avatar-lap` −8px, the `+N` chip and the tallest bar inside
one column without the stack climbing out of the plot. One column per day — every day in
the window, including the empty ones, because a gap in a job search is information and a chart that
drops empty days draws effort that did not happen.

| part            | treatment                                                                                                                                                                                           |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| bar (count > 0) | `--color-ink`, `--radius-full`, max width 10px, height `count / peak × 96px` with a 10px floor so one application is still a bar                                                                    |
| empty day       | a `--dot-day` 10px `--color-chart-dot` `rgba(23,23,23,0.16)` dot on the baseline. It is the bar's own width, so the baseline reads as one deliberate axis of equal marks with bars rising out of some of them. At 6px and 0.12 it read as dust. Past 30 days it drops to `--dot-day-wide` 6px, because a 90-day column is about 5px wide and a 10px dot there joins into a solid rule instead of marking a day |
| avatar          | 24px circle, 2px `--color-surface` ring, stacked upward with `--avatar-lap` −8px overlap, newest nearest the bar. The API returns a day's companies oldest-first, so the stack takes the *last* `n` of them                                  |
| monogram        | the same circle in `--color-tile` with the company's initial in `--color-ink-3` at 11px/600. **This is a normal state, not an error state** — three of the nine companies on the board have no icon |
| overflow        | a `--radius-full` `--color-tile` chip, mono 11px, `+N`, directly above the stack                                                                                                                    |
| date label      | mono `--text-tag` at `--color-ink-3`, every `ceil(days / 7)`-th column, with the last always "Today"                                                                                                |

**The stack shrinks with the range**, because at 90 days a column is three pixels wide: 6 avatars at
3–14 days, 2 at 30, 1 at 90. Six rather than three at the narrow ranges because the real board puts
most of a week's applications on one day, and three icons under a `+6` is one small cluster in a
large card — the page should read as active with the icons it actually has. The cap is vertical
room, not taste: six is what `--plot-h` holds beside the tallest bar. 30 and 90 are unchanged,
where the constraint is a column's width rather than the card's height. Avatars only ever appear above a day with activity, so a wide range
reads as a sparse line of dots with one marked cluster — which is what the data is.

Icons come from `/api/icon/{company}` on our own origin and are requested **only when `has_icon` is
true** (§7.2). The whole column carries a `title` of "Oct 12 · 9 sent"; the avatars carry the
company's name.

**One day with every application on it is a correct state**, not a broken one — the card must look
deliberate with a single bar and a row of dots, and nothing may be invented to fill it (§14).

### 7.16 The dashboard greeting

The dashboard's page title is a greeting, not the word "Dashboard": `Good morning`, `Good afternoon`
or `Good evening`, followed by `, {name}` when the profile has one.

| part           | hours, local  |
| -------------- | ------------- |
| Good morning   | 05:00 – 11:59 |
| Good afternoon | 12:00 – 17:59 |
| Good evening   | 18:00 – 04:59 |

The clock is the browser's, because the greeting is about where the person is sitting. **With no
name set the greeting stands alone** — "Good evening", never "Good evening, friend", never a
placeholder, and never the email address. The name is edited in Profile & settings and is the only
place it comes from.

### 7.17 Profile menu

A 32px `--radius-full` `--color-ink` circle alone in the page header's top band (§6.2), carrying the
initials of `profile.name` in `--color-ink-inverse` at 11px/600 — up to two, from the first two
words. **With no name it shows a neutral person glyph**, never a placeholder letter and never the
email address. There is no avatar image anywhere in this app and none is invented.

It opens a 224px `--radius-lg` menu (§7.7's treatment) with the name and a one-line caption at the
top, then:

| item               | behaviour                                                                                                                                  |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Profile & settings | navigates to the combined screen (§11.6)                                                                                                   |
| Edit target roles  | navigates to onboarding, which is where roles are chosen                                                                                   |
| Log out            | **rendered disabled** — `aria-disabled`, `opacity: 0.45`, `cursor: not-allowed`, with a `title` saying there are no accounts to log out of |

Log out is disabled rather than live-and-inert on purpose: a live item that does nothing when
clicked reads as a bug, and a disabled one with a reason reads as a fact about the app. There is no
auth here and the menu should not imply there is.

**This is the only profile and settings entry.** The rail's bottom control was briefly an
avatar-style link to the same screen; it is gone, because a direct link and a menu both landing on
`/settings` is the duplication the header menu was meant to resolve, and the menu is the richer of
the two. The rail's bottom now carries only the connectivity dot.

### 7.18 Empty states

A real sentence at `--text-lead` on `--color-ink-2`, then one action that fills the screen. Centered
in its container, `--space-12` of vertical padding. Never seed sample rows to make a screen look
populated. Coach's empty state carries a gradient panel rather than an image.

### 7.19 Applications by status

The right-hand card of the chart row, `--radius-xl`, `--space-5` padding. A `--text-section` title,
`--space-3`, a `--donut` 112px conic-gradient donut with a `--donut-ring` 15px ring and the sent
count at `--text-display` in its hole, `--space-3`, then one `--legend-h` 36px
`--color-surface-sunk` row per status — Awaiting reply, Interviewing, Offer, Rejected — with
`--space-1` between them.

**It shares a grid row with the activity chart, so it carries that row's height and not its own
idea of one.** When the chart shortens, this shortens with it: the donut was 156px and the legend
rows 40px while the card stood at 435, which was the chart's height rather than anything this card
needed. At 112 / 36 the card is 359 and its content reaches the bottom padding.

---

## 8. States

Every component defines all of these. A state that isn't listed doesn't exist.

| state    | treatment                                                                                                                                                                                                                                                                        |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| hover    | rows `--color-row-hover`; controls `--color-hover`; rail `--color-rail-hover`. `--duration-hover` 100ms on `background-color` only. All hover styling lives under `@media (hover: hover)` — Tailwind 4's `hover:` already compiles there                                         |
| pressed  | `scale(0.96)` over `--duration-quick` with `ease-out`, only on onboarding role chips and primary buttons. Never on a disabled control: use `enabled:active:`. `-webkit-tap-highlight-color: transparent` wherever a control draws its own press                                  |
| selected | row: `--color-selected` fill plus a 2px × 40px `--color-ink` marker at the row's left edge. Nav: §6.1. Segment: §7.6. Selection always has a shape cue, not only a fill                                                                                                          |
| focus    | `outline: none; box-shadow: 0 0 0 3px var(--color-ring)` plus `border-color: var(--color-ink)`. Applied via `:focus-visible` globally. On the dark rail the ring is `rgba(255,255,255,0.45)` instead — specify it on the rail, don't let the global rule disappear into the dark |
| loading  | a `--color-tile` block at the element's exact final size and radius, pulsing opacity 1 → 0.6 → 1 over 1200ms `ease-in-out`. Never a spinner inside a row. Never a layout that reflows when data lands: the skeleton is the same height as the row                                |
| empty    | §7.15                                                                                                                                                                                                                                                                            |
| error    | an inline strip at the top of the affected card: `rgba(179,38,30,0.08)` fill, `#B3261E` text at `--text-body`, a 16px warning glyph, `--radius-md`, entering with `--animate-in`. Never a toast, never a modal. The sentence says what failed and what to do                     |
| disabled | `opacity: 0.45`, `cursor: not-allowed`, no hover, no press, no focus ring on a non-focusable element                                                                                                                                                                             |
| offline  | the rail dot turns `--color-offline` and its `aria-label` changes to "API offline". Nothing else in the UI changes color                                                                                                                                                         |

---

## 9. Motion

Carried forward from the previous document. It was written against `better-ui` and `motion-design`
and the new density does not change it. The two additions are marked.

The archetype is **Corporate**: clean, predictable, functional. This is a board someone scans every
day, so motion confirms what just happened and never competes with reading. No bouncing, no
overshoot, no loops, no ambient or decorative motion anywhere.

Three constants, all `@theme` tokens. Use the tokens, never a raw curve or a millisecond literal in a
component.

**Signature easing** — `--ease-brand` `cubic-bezier(0.2,0,0,1)`, the default everywhere.

- It is also wired to `--default-transition-timing-function`, so a bare `transition-*` class already
  uses it and needs no `ease-` utility.
- Two exceptions, both deliberate: `--ease-panel` `cubic-bezier(0.32,0.72,0,1)` for the detail
  panel's width, and `ease-out` on a press, which `better-ui` fixes as an exact value.

**Duration palette** — three tiers plus one for hover.

- `--duration-hover` `100ms` — row hover, and anything else that fires while scanning
- `--duration-quick` `150ms` — the default; presses, fills, chevrons, segment and filter state
- `--duration-standard` `300ms` — the detail panel's width, and _(new)_ the backdrop's fade-in
- `--default-transition-duration` is `--duration-quick`, so a bare `transition-*` is 150ms and only
  the off-default tiers name a duration

**Entrance pattern** — one recipe, 150ms, opacity with `translateY(4px)` and `scale(0.98)`.

- `--animate-pop` enters downward from its trigger: menus and popovers
- `--animate-in` enters upward: inline inputs, empty states, a save confirmation, an error strip
- Nothing else animates in. **Rows never stagger or fade.** A table of 4,000 rows that animates on
  every load or filter change is noise, not polish. This does not change at 64px rows — bigger rows
  make a stagger worse, not better.

**The backdrop fade.** The only motion the imagery is allowed. `.backdrop-img` starts at
`opacity: 0` and transitions to `1` over `--duration-standard` with `--ease-brand` on its `load`
event. Opacity only — no scale, no blur animation, nothing that moves. It runs **once per session,
not once per route**: the backdrop is mounted in the shell above the router, so a route change does
not remount it and the photograph never fades out and back. Changing the background in Profile &
settings swaps the `src` on the same element, which the browser paints when the new file decodes;
there is no second fade. Skipped entirely under reduced motion.

**The rail tooltip (new).** `opacity` 0 → 1 and `translateX(-4px)` → `0` over `--duration-quick`
150ms on `--ease-brand`, entering and leaving. It is a high-frequency hover, so it never gets the
standard tier. Under `prefers-reduced-motion` the translate is dropped and the global rule collapses
the fade. It is CSS only: no state, no timers, no delay — a delay on a navigation tooltip is a
guessing game the user loses.

**Skeletons do not animate in or out.** A skeleton is replaced by its content with no cross-fade,
because the point of it is that nothing in the layout changes at that moment. The only motion it has
is the §8 loading pulse.

**Other rules**

- Press is `scale(0.96)` over `--duration-quick`, gated behind `motion-safe:`, on onboarding role
  chips and primary buttons only. A disabled control never scales.
- Exits are instant. Menus, the panel and empty states unmount without motion, which carries no
  information here.
- Route changes are instant and there is no page transition. What makes them feel smooth is not
  animation but **everything that does not move**: the rail and the backdrop live above the router
  and never remount, `/api/filters` is fetched once for the app rather than once per page, and every
  list, chart and card holds its final height with a skeleton while its data is in flight. Measured
  layout shift on a route change is 0.000 on every route except Profile & settings, which is
  0.00014. A skeleton that reserves the right height beats a fade over a jumping layout; reserving
  the space beats animating the move.
- Transition named properties only, never `all`.
- Drive interactive state with transitions, not keyframes, so a reversal mid-flight retargets.
  Keyframes are reserved for the two one-shot entrances and the loading pulse.
- Icon stroke is 1.5 beside regular text and 2 beside semibold, which is why the active rail icon is
  heavier than the rest.
- Respect `prefers-reduced-motion`: the global rule in `index.css` covers every transition and
  animation, and the press scale is additionally `motion-safe:`.

---

## 10. Accessibility

- **Contrast:** §2.5. The floor is 4.5:1 below 24px, 3:1 at 24px/600 and above and for control
  boundaries, measured against the worst-case composite `#EAEAEA` — not against white.
- **Focus:** every interactive element shows the §8 focus ring. The rail gets the light ring. Focus
  order follows the DOM; the detail panel traps nothing, because it is a sibling panel and not a
  dialog, but it does move focus to its own header when it opens and returns focus to the originating
  row when it closes.
- **Hit areas:** 40px minimum on anything clickable, 36px on a ghost icon button with at least 8px of
  clear space around it. The 44px rail buttons and 64px rows are comfortably over. A row's action
  button is in the DOM at all times and only its _opacity_ is hover-dependent, so it is always
  reachable by keyboard.
- **Reduced motion:** the global `prefers-reduced-motion: reduce` block stays. Under it, the backdrop
  image appears without a fade, the press scale does not run, the rail tooltip appears without its
  translate, and the loading pulse holds at a constant `--color-tile`.
- **Color is never the only channel.** Status pills carry a label beside the dot. Delta chips carry
  an arrow. The connectivity dot carries an `aria-label`. The active rail item carries a shape marker
  as well as a fill: its glyph goes from 45% to 100% white and its stroke from 1.5 to 2.1, and
  `aria-current="page"` states it outright. Rail tooltips appear on `:focus-visible` as well as on
  hover, so the icon-only rail is labelled for the keyboard too.
- **Images:** every decorative image is `alt=""` and `aria-hidden="true"`. The sparkline is
  `aria-hidden`; its value is already in the KPI number beside it.
- **Forced colors:** every shadow ring has a transparent border beneath it (§5.3). Backdrops and
  scrims disappear in forced-colors mode and the page must still be correct — which it is, because
  nothing readable was on them.

---

## 11. Screens

Every screen carries the one chosen backdrop (§3.1) and the floating rail, except onboarding, which
carries the backdrop without the rail.

1. **Dashboard** (`/`) — title is the greeting (§7.16). KPI row of four cards plus
   the theme's hero companion; then a two-column body: the activity chart (§7.15) and "Top of your board"
   on the left, "Applications by status" and the target-roles card on the right; then "Your
   applications". The target-roles card is **last in its column on purpose** — its height is the one
   nobody can know before the fetch, so nothing sits under it to be pushed.
2. **Detail panel** — the same screen with a row selected, the panel open at 460px.
3. **All listings** (`/listings`) — one `--radius-2xl` container card holding the filter toolbar
   (Industry, Role, Level, Degree, Status, Sort, search), the header row, 64px rows and "Load more".
   The Status filter includes "Ignored", which is how an ignored listing is found again.
4. **Tracker** (`/tracker`) — the segmented control above the container card, rows grouped under
   sticky status headers, "Add a job" in the page header. Tracking is separate from browsing; never
   merge them back.
5. **Coach** (`/chat`) — a placeholder card saying it is a later phase.
6. **Profile & settings** (`/profile`, and `/settings` renders the same screen) — the profile card,
   "What you are looking for" with the name and degree fields, "Target roles", and **Customize**,
   which holds the background picker. The header's profile menu (§7.17) lands here. One screen rather
   than two, because the only setting the app has is the background and a page holding one row is
   not a page; both paths resolve so neither URL goes dead.
7. **Onboarding** (`/onboarding`) — title at `--text-title-lg`, the role chips, and the "Other"
   chip. The one screen with no rail.

**The background picker** (inside Profile & settings) is modelled on the reference's Customize
panel: a card header with a 36px icon tile, a title and a close button; then a bordered sub-card row
showing the current background as a small grey label over a bolder value with a thumbnail at the
right; then a bordered sub-card holding all nine as a 3-column grid of image thumbnails, each
`--radius-md`, 88px tall, labelled with its name and its tone. The current one takes a 2px
`--color-ink` ring and an `--color-ink` check badge. Selecting one applies it immediately and
`POST`s it; a failed write reverts the choice and shows the §8 error strip rather than lying about
what is stored.

## 12. Data rules

Unchanged from the previous document and still binding.

- Render `display_title`, never `title`. `title` keeps the season, team and degree; it belongs in the
  tooltip and in the panel's "Raw posting title".
- `posted_at`, `level`, `education`, `term` and `industry` can all be empty. Every row must look right
  with none of them set.
- `location` can be hundreds of characters. Truncate in rows; wrap in the panel.
- `industry_rank` is 1-based preference and `999` means unranked — show "unranked", not 999.
- `copies` above 1 means duplicate postings were collapsed; say so in the panel.
- `full_text` is 0 for almost everything, which the panel reports as "link only".

---

## 13. Attribution

Adzuna rows must carry "Jobs by Adzuna" wherever they surface: a mono `--text-meta` line under any
table that contains one, and beside the Source property in the panel. This is a licence term, not a
design choice, and it survives any restyle.

---

## 14. Don't

- No dark mode. The rail is dark; the app is not.
- No blue. The previous accent is gone from the palette entirely.
- No second accent use per screen.
- No text on a photograph outside the page title and its subtitle (§2.5), the hero card (§7.11)
  and §7.12.
- No card below `--color-surface-veil`'s 0.94 opacity.
- No `backdrop-filter` on a card (§2.1), no neon, no heavy shadows.
- No white page title over a bright background, and no dark one over a dark background: the ink
  follows `tone` (§2.5) and nothing else.
- No company logos; the icon tile stays small and neutral (§7.2).
- No emoji in the UI except the icon-tile fallback.
- No new dependency — no motion library, no component library, no icon package. Icons stay inline SVG
  paths in `src/lib/icons.ts`.
- No invented values. If the design asks for something the API does not have, leave it out and say
  why, rather than filling it with a placeholder.

---

## 15. Open questions

These are the decisions the brief did not settle. I made a provisional call on each so the document
is implementable, but each one is flagged rather than buried, and any of them can be overturned
before the implementation task starts.

1. ~~**Where the sidebar's content went.**~~ **Decided: 72px icon rail.** Target roles become a card
   on the dashboard's right column; the API host moves to Profile; "Edit" becomes a button on that
   card; connectivity survives as a dot at the bottom of the rail. The 232px alternative, which would
   have kept the role counts permanently on screen, was considered and rejected in favour of the
   horizontal room the 64px rows need.
2. **The `new` status pill's color.** Blue left the palette and orange is reserved. _Provisional:_
   `new` becomes a neutral off-black pill, and the accent is spent on the _count_ of new listings in
   the KPI row. The cost is that a new row no longer announces itself in the table by color — it still
   has the unread dot.
3. **`saved` sits near the accent.** `#FF9500` amber and `#FF4E02` orange are neighbours.
   _Provisional:_ keep `saved` at its current amber, used only as a 13%-opacity tint and never as a
   solid fill, so the two never compete as solids. If they still read as the same thing on screen,
   `saved` should move to a yellow-green rather than the accent moving.
4. ~~**Nine image slots is a lot of approvals.**~~ **Overtaken.** Per-page backdrop slots are gone.
   There is one backdrop, chosen from nine shipped photographs in Profile & settings (§3.2), plus
   a hero companion per theme and `profile-cover` as content images. Build against the gradient fallbacks
   regardless — they are what renders under `prefers-reduced-transparency`.
5. **The sparkline has no data source.** §7.10 specifies one because the reference has one, but
   nothing in the API returns a per-KPI time series today. _Provisional:_ ship KPI cards without
   sparklines and add them when there is real data. Do not fake the curve — §14.
6. **The activity rail has no data source either.** There is no event log in the API. _Provisional:_
   on the dashboard, the right column holds the target-roles card and "Your applications" instead,
   and the activity rail stays specified here for when an event log exists.
7. ~~**Reduced transparency.**~~ **Done.** Under `prefers-reduced-transparency: reduce` the backdrop
   image is dropped and the gradient fallback carries the page, with cards at full `--color-surface`.
8. **The hero card is still the old dark abstract.** It is a card, not the backdrop, so the new
   photographs do not reach it — but a near-black card beside a bright meadow is a choice nobody
   made on purpose. _Provisional:_ leave it; revisit if it reads as a leftover.
9. **The greeting pushes "Dashboard" out of the UI.** The page no longer names itself anywhere
   except the rail tooltip. _Provisional:_ accept it — one person, one app, and the tooltip covers
   the one case where the name is needed.
