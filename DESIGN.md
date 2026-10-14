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

1. **The photograph is a page-level backdrop. It is never a surface.** It sits behind the whole page
   at `z-index: 0`, fixed, scrimmed and blurred. It does not move, parallax, loop or animate beyond
   a single fade-in on first paint.
2. **Everything readable rides on a near-opaque surface above it.** Cards, rows, the toolbar, the
   detail panel, menus. No body text, table row, table header, form label, input, chip or helper
   line ever sits directly on a photograph.
3. **There is exactly one exception and it is specified by name:** the hero image card (§4.7), which
   is a full-bleed photograph carrying one large number and one label in white, over a mandated dark
   scrim, at a mandated minimum size. Category-tile titles (§4.8) follow the same rule. Nothing else
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

| token | value | use |
| --- | --- | --- |
| `--color-page` | `#FAFAFA` | the page background, and the base color under every backdrop and scrim |
| `--color-surface` | `#FFFFFF` | cards, rows, the toolbar, the detail panel, menus — opaque, on pages with no backdrop |
| `--color-surface-veil` | `rgba(255,255,255,0.94)` | the same surfaces on a page that has a backdrop. 0.94 is the floor; never lower it. The page scrim is light (§3.1), so the card is the only thing standing between a photograph and a line of text |
| `--color-surface-sunk` | `#F4F4F4` | table headers, group headers, the inside of an inset search field |
| `--color-tile` | `#EFEFEF` | company icon tile, chart stubs, avatar fallbacks |
| `--color-rail` | `#171717` | the dark left rail |
| `--color-rail-hover` | `rgba(255,255,255,0.08)` | rail icon hover |
| `--color-rail-active` | `rgba(255,255,255,0.14)` | rail icon active fill |

Cards on a backdrop page use `--color-surface-veil` **plus** `backdrop-filter: blur(20px)
saturate(1.05)`. The blur is what makes 0.94 read as solid rather than as a smeared photo. Where
`backdrop-filter` is unsupported, the fallback is `--color-surface` at full opacity — specify both.

### 2.2 Ink

| token | value | contrast on `#FFFFFF` | use |
| --- | --- | --- | --- |
| `--color-ink` | `#171717` | 16.0:1 | titles, row primary text, numbers, primary button fill |
| `--color-ink-2` | `#323232` | 11.9:1 | body copy, secondary row text, table values |
| `--color-ink-3` | `#666666` | 5.7:1 | labels, meta, timestamps, column headers, placeholders. **The lowest tier allowed for any text anywhere, including over a backdrop** |
| `--color-ink-4` | `#8A8A8A` | 3.5:1 | **never informational text.** Disabled labels, inactive rail icons, decorative glyphs, chart gridlines |
| `--color-ink-inverse` | `#FFFFFF` | — | text on `--color-ink` and on the hero image card |

### 2.3 Lines

| token | value | use |
| --- | --- | --- |
| `--color-line` | `rgba(23,23,23,0.08)` | card borders, control borders |
| `--color-line-soft` | `rgba(23,23,23,0.06)` | dividers inside a card, between table rows |
| `--color-line-strong` | `rgba(23,23,23,0.14)` | input borders, menu borders, outline buttons. Meets the 3:1 non-text floor |

### 2.4 Accent and state fills

| token | value | use |
| --- | --- | --- |
| `--color-accent` | `#FF4E02` | the one hot number per screen; the unread dot. **Never a background for text smaller than 24px, and never a text color at any size** |
| `--color-accent-ink` | `#B83300` | when accent must be *text* — 6.0:1 on white, 5.0:1 on the worst-case card |
| `--color-accent-soft` | `rgba(255,78,2,0.10)` | the tint behind an accent number |
| `--color-hover` | `rgba(23,23,23,0.04)` | control and menu-item hover |
| `--color-row-hover` | `rgba(23,23,23,0.03)` | table row hover |
| `--color-selected` | `rgba(23,23,23,0.06)` | the selected row, with a 2px `--color-ink` left marker |
| `--color-track` | `rgba(23,23,23,0.06)` | segmented-control track, secondary button fill |
| `--color-ring` | `rgba(23,23,23,0.28)` | focus ring |

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

| color | on `#EFEFEF` | verdict |
| --- | --- | --- |
| `--color-ink` `#171717` | 14.9:1 | pass |
| `--color-ink-2` `#323232` | 10.7:1 | pass |
| `--color-ink-3` `#666666` | 4.8:1 | pass, with no margin — do not darken the page or lighten this token |
| `--color-ink-4` `#8A8A8A` | 2.9:1 | fails; non-text only, as stated |
| `--color-accent-ink` `#B83300` | 5.0:1 | pass |

**Text directly on the backdrop.** Page titles, the date beside them, and the "Jobs by Adzuna"
line sit on the photograph, not on a card. On a backdrop page they are `--color-ink-inverse`
`#FFFFFF`, never an ink token. Measured on the approved asset through `--scrim-page`, white reaches
**4.7:1** against the brightest part of its top third, so it passes at every size rather than only
at display sizes. Two rules follow and both are load-bearing:

- A backdrop whose top third measures brighter than **L 0.18** through the scrim is rejected and
  re-generated. That is the threshold at which white text drops under 4.5:1.
- No body text, table row, form label or control ever sits on the backdrop. Those live on cards.
  The backdrop carries titles and nothing else.

On a page with no backdrop, titles are `--color-ink` as usual.

**How to verify a screen:** open devtools, set the backdrop `<img>` to `background: #000` with
`opacity: 1` and no scrim, then run the contrast checker on every text node on the page. If anything
below 24px reads under 4.5:1 in that state, it is a bug — not a lighting problem to be solved by
choosing a brighter photograph. Do this once per new screen and once per new image slot.

### 2.6 Status palette

Unchanged hues and meanings. These are the backend's keys, which is what `POST /api/status` accepts.

| key | label | text | background | dot |
| --- | --- | --- | --- | --- |
| `new` | New | `#171717` | `rgba(23,23,23,0.07)` | `#171717` |
| `saved` | Saved | `#9A5400` | `rgba(255,149,0,0.13)` | `#FF9500` |
| `applied` | Applied | `#1E7A34` | `rgba(52,199,89,0.14)` | `#34C759` |
| `interviewing` | Interviewing | `#7A3DA8` | `rgba(175,82,222,0.12)` | `#AF52DE` |
| `offer` | Offer | `#0B6E80` | `rgba(48,176,199,0.15)` | `#30B0C7` |
| `rejected` | Rejected | `#666666` | `rgba(23,23,23,0.05)` | `#AEAEB2` |
| `hidden` | Archived | `#8A8A8A` | `rgba(23,23,23,0.04)` | `#C7C7CC` |

`hidden` takes a listing off both the board and the tracker, so the status menu never offers it; it
is reached only through Archive, and exists in this table because a stored `hidden` row still turns
up in Search and must draw as something. A status key the table does not know draws gray and reads
"Unknown", never "New".

Backend connectivity dot: `--color-online` `#1E7A34`, `--color-offline` `#B3261E`. Both are the text
weight of their hue, because the dot sits on the dark rail where a bright `#34C759` glares.

**Changed from:** `new` was `#0066CC` blue and `rejected`/`hidden` used `#6E6E73`/`#8E8E93`. Blue has
left the palette entirely, so `new` is now the neutral ink pill; the accent is reserved for the
*count* of new listings, not for the per-row pill. Online/offline dots were `#34C759`/`#FF3B30`.

### 2.7 Deleted tokens

Every `--color-accent*` blue (`#0A84FF`, `#0077ED`, `#0066CC`), `--color-bg` `#F5F5F7`,
`--color-sidebar` and the `.sidebar-blur` and `.glow` component classes. Nothing may reference them
after the implementation task.

---

## 3. Imagery

### 3.1 How a backdrop is built

Assets are Higgsfield-generated and approved shot by shot. Design and build against the named
placeholders below; the layout must be reviewable before any image exists.

Every backdrop page renders exactly this structure. It is three layers and no more.

```
<div class="backdrop" aria-hidden="true">   /* fixed, inset 0 0 0 var(--rail-w), z-index 0 */
  <div class="backdrop-fallback"></div>     /* the CSS gradient, always present */
  <img class="backdrop-img" ... />          /* absent until the asset is approved */
  <div class="backdrop-scrim"></div>        /* always present, above both */
</div>
```

| layer | treatment |
| --- | --- |
| `.backdrop` | `position: fixed; inset: 0 0 0 var(--rail-w); z-index: 0; overflow: hidden; pointer-events: none` |
| `.backdrop-fallback` | the slot's gradient, `position: absolute; inset: 0` |
| `.backdrop-img` | `width/height: 100%; object-fit: cover; filter: saturate(0.80) blur(10px); transform: scale(1.04)` — the scale hides the blur's soft edge. Fades in once on load (§7) |
| `.backdrop-scrim` | `background: var(--scrim-page)` |

Page content sits in a sibling at `z-index: 1`. The 10px blur is on the image, not a
`backdrop-filter`, because it must composite once rather than on every scroll frame.

**Why the veil is 15% and not 85%.** An earlier draft of this document veiled the backdrop at
0.80–0.92. Measured against the approved asset, that leaves 0.3–0.8% visible variation: the image is
gone and the page is flat off-white. A page backdrop only exists if you can see it. Readability is
not the scrim's job here — it is the cards' job, and they are opaque. So the veil is light enough
that the photograph reads, and the discipline moves to §3.3.

**Scrim tokens**

| token | value |
| --- | --- |
| `--scrim-page` | `linear-gradient(180deg, rgba(250,250,250,0.12) 0%, rgba(250,250,250,0.15) 55%, rgba(250,250,250,0.20) 100%)` |
| `--scrim-image-card` | `linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.25) 45%, rgba(0,0,0,0.62) 100%)` |
| `--backdrop-filter` | `saturate(0.80) blur(10px)` |
| `--backdrop-scale` | `1.04` |

**Asset rules for every slot:** JPEG, sRGB, `loading="eager"` for backdrops and `decoding="async"`,
2× the slot's CSS size, under 400 KB after export, stored in `web/public/img/`, filename equal to the
slot name. Every `<img>` that is decoration carries `alt=""` and `aria-hidden="true"`; the hero card's
image is decoration too, because its number is real text beside it.

### 3.2 The slots

Nine slots. Each has a name, a ratio, a subject direction, its scrim, and a fallback gradient that
ships whether or not the image does.

**Two are shipped**: `backdrop-dashboard` and `hero-card-dashboard`, both in `web/public/img/`. The
other seven run on their fallback gradients and must look deliberate that way — that is the whole
reason the fallbacks are specified. Do not treat a gradient slot as unfinished.

---

**`backdrop-dashboard`** — 16:9, 1920×1086, file `img/backdrop-dashboard.jpg` — **asset shipped**

*Subject / mood:* abstract deep-green silk folds dissolving into black, soft volumetric light, no
object, no horizon, no face. The frame must be busy nowhere; the top third especially must stay
flat, because the title and the KPI row sit over it.
*Measured:* raw luminance 0.002–0.025; through `--scrim-page`, white title text reaches 4.7:1.
Replacing this asset means re-measuring against the L 0.18 ceiling in §2.3.
*Scrim:* `--scrim-page`.
*Fallback:* `radial-gradient(120% 90% at 18% -10%, #F2EFEA 0%, #FAFAFA 55%, #FAFAFA 100%)`

---

**`backdrop-listings`** — 16:10, 2560×1600, file `img/backdrop-listings.jpg`

*Subject / mood:* an aerial or very-long-lens abstraction — a city block from above, a runway of
light, a field pattern. Texture without subject. Cooler than the dashboard. The table covers most of
this image; it is a border treatment more than a picture.
*Scrim:* `--scrim-page`.
*Fallback:* `radial-gradient(130% 100% at 80% -20%, #ECEFF2 0%, #FAFAFA 60%, #FAFAFA 100%)`

---

**`backdrop-tracker`** — 16:10, 2560×1600, file `img/backdrop-tracker.jpg`

*Subject / mood:* progression made abstract — a stair edge in raking light, a staggered facade, a
long shadow sequence. Must read as forward motion without a literal arrow. Warm-neutral, higher
contrast permitted in the lower third only, which the scrim closes to flat.
*Scrim:* `--scrim-page`.
*Fallback:* `linear-gradient(165deg, #F3F0EC 0%, #FAFAFA 45%, #FAFAFA 100%)`

---

**`backdrop-coach`** — 16:10, 2560×1600, file `img/backdrop-coach.jpg`

*Subject / mood:* the most atmospheric of the set, because the page is nearly empty — dusk through
glass, haze over water, a soft gradient of a real place. No subject at all. Coach is a placeholder
page, so this is the one backdrop allowed to be the most interesting thing on its screen.
*Scrim:* `--scrim-page`.
*Fallback:* `linear-gradient(195deg, #EDEFF3 0%, #F6F5F4 50%, #FAFAFA 100%)`

---

**`backdrop-profile`** — 16:10, 2560×1600, file `img/backdrop-profile.jpg`

*Subject / mood:* paper, linen, a plan chest, a wall of neutral texture. Close, tactile, still. The
profile is a form; the backdrop must be the quietest of the six.
*Scrim:* `--scrim-page`.
*Fallback:* `linear-gradient(180deg, #F5F3F0 0%, #FAFAFA 70%, #FAFAFA 100%)`

---

**`backdrop-onboarding`** — 16:10, 2560×1600, file `img/backdrop-onboarding.jpg`

*Subject / mood:* the brightest and most open of the six — horizon, a lot of sky, an early hour. This
is the first screen anyone sees and the only one that gets to feel like a beginning. Still no faces,
no text.
*Scrim:* `--scrim-page`.
*Fallback:* `radial-gradient(110% 80% at 50% -20%, #F0F4F6 0%, #FAFAFA 60%, #FAFAFA 100%)`

---

**`hero-card-dashboard`** — 3:2, 960×638, file `img/hero-card-dashboard.jpg` — **asset shipped**

The one place text sits on a photograph. Modelled on Juney's "€82.6k Total cashflow" card: a
full-bleed image card at the end of the KPI row, carrying the headline count of new listings.

*Subject / mood:* abstract, flowing, close — liquid, smoke, folded fabric, a long-exposure light
form. No horizon, no object, no face. **The asset is approved only if its bottom 45% is already dark
and even.** The scrim darkens it further; it must not be doing the whole job alone.
*Scrim:* `--scrim-image-card`, as an `::after` filling the card.
*Text allowed on it:* the number at `--text-display` 40px/600 in `--color-ink-inverse`, one label at
16px/500 at `rgba(255,255,255,0.80)`, and up to two pill buttons. Nothing else, ever.
*Floor:* white on the scrimmed lower third must measure ≥ 7:1. Check it on the approved asset, not
on the fallback. The shipped asset measures **20.1:1 worst case** across its bottom 45%, before the
scrim. A rejected candidate measured 1.6:1 there — it looked fine and was not. Measure, do not look.
*Fallback:* `linear-gradient(145deg, #2E2E2E 0%, #171717 55%, #000000 100%)` — the card is designed
dark, so the fallback is a dark card and the text does not move.

---

**`coach-empty`** — 4:3, 1200×900, file `img/coach-empty.jpg`

The illustration inside the Coach placeholder card. Sits inside a card, 320px wide, with its own
`--radius-md` clip. Not a backdrop and carries no text.
*Subject / mood:* a single quiet object in soft light — a notebook edge, a chair, a doorway. Implies a
conversation that hasn't happened yet.
*Scrim:* none; it carries no text. Apply the image outline in §3.3.
*Fallback:* `linear-gradient(135deg, #EFEFEF 0%, #E4E4E4 100%)`

---

**`profile-cover`** — 4:1, 1600×400, file `img/profile-cover.jpg`

A banner across the top of the profile card, behind nothing — the avatar and name sit *below* it, on
the card, not on the image.
*Subject / mood:* the same material family as `backdrop-profile`, cropped tighter. Must tile visually
with it without matching it exactly.
*Scrim:* a 1px inner line only — `inset 0 -1px 0 var(--color-line)` at its bottom edge.
*Fallback:* `linear-gradient(90deg, #F0EDE9 0%, #F6F6F6 50%, #EFF1F3 100%)`

### 3.3 Image outlines

Every content image — `coach-empty`, `profile-cover`, the hero card — takes `outline: 1px solid
rgba(0,0,0,0.1); outline-offset: -1px`, per `better-ui`. Never a palette near-black and never the
accent: a tinted outline shows as a colored fringe. Backdrops are exempt; they have no visible edge.

### 3.4 Things imagery may never do

No image behind a table body, a form or the detail panel's content. No image in a row, a pill, a
chip, a menu or a button. No company logos (see §5.2 — the privacy reason is unchanged). No parallax,
no Ken Burns, no video, no loop. No image slot that isn't in §3.2.

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

| token | size | line | weight | tracking | use |
| --- | --- | --- | --- | --- | --- |
| `--text-display` | 40px | 1.05 | 600 | -0.032em, tabular-nums | KPI numbers, the hero card number |
| `--text-title` | 32px | 1.15 | 600 | -0.026em | page titles |
| `--text-title-lg` | 38px | 1.1 | 600 | -0.028em | onboarding title only |
| `--text-section` | 20px | 1.25 | 600 | -0.018em | card titles, panel title, group headers |
| `--text-lead` | 16px | 1.5 | 400 | -0.01em | page subtitle, panel body, empty-state sentence |
| `--text-row` | 15px | 1.35 | 500 | -0.008em | row primary text (role, company). 600 when unread |
| `--text-body` | 14px | 1.45 | 400 | -0.006em | the default |
| `--text-control` | 14px | 1 | 500 | -0.004em | buttons, filter chips, menu items, inputs |
| `--text-meta` | 13px | 1.3 | 500 | 0 | location, timestamps, counts, secondary row line |
| `--text-label` | 12px | 1.2 | 600 | 0.04em, uppercase | column headers, KPI card labels |
| `--text-tag` | 12px | 1 | 500 | 0 | title tags, delta chips (mono) |

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

A 4px scale. Use the token, not the number.

| token | value | typical use |
| --- | --- | --- |
| `--space-1` | 4px | icon-to-label inside a pill |
| `--space-2` | 8px | tag gaps, chip internals |
| `--space-3` | 12px | control internals, row internal stacking |
| `--space-4` | 16px | card padding (small), grid gap |
| `--space-5` | 20px | — |
| `--space-6` | 24px | card padding (default), gap between cards |
| `--space-8` | 32px | page gutter, gap between card and table |
| `--space-10` | 40px | page gutter (wide), between sections |
| `--space-12` | 48px | between major sections, bottom of scroll area |
| `--space-16` | 64px | onboarding block spacing |

**Changed from:** card padding 20px → 24px; page gutter 32px → 40px; between-section gap 22px →
`--space-10` / `--space-12`.

### 5.2 Radius

Measured off the crops. Juney's radii are generous and its controls are capsules.

| token | value | use |
| --- | --- | --- |
| `--radius-xs` | 6px | title tags, checkboxes |
| `--radius-sm` | 8px | company icon tile (small), delta chip |
| `--radius-md` | 12px | rail icon buttons, inputs, menu items, company tile (panel) |
| `--radius-lg` | 16px | menus, popovers, inner cards, the segmented track |
| `--radius-xl` | 20px | KPI cards, the hero image card, the activity rail card |
| `--radius-2xl` | 28px | the page's big container cards (table card, chart card), the detail panel |
| `--radius-full` | 999px | every button, every filter chip, every status pill, every segment, every onboarding chip |

Apply `better-ui`'s concentric rule: where a card is padded and holds a nested surface, the outer
radius is the inner radius plus the padding. A `--radius-2xl` 28px card with `--space-3` 12px padding
holds a `--radius-lg` 16px inner surface. Past 24px of padding, treat the layers as separate and keep
each one's token.

**Changed from:** nearly everything. Controls were 8px and are now capsules; cards were 16px and are
now 20–28px; pills were 11–13px and are now `--radius-full`.

### 5.3 Shadows and borders

| token | value | use |
| --- | --- | --- |
| `--shadow-card` | `0 1px 2px rgba(23,23,23,0.04), 0 12px 32px -16px rgba(23,23,23,0.10)` | KPI cards, container cards, the hero image card |
| `--shadow-float` | `0 16px 40px -8px rgba(23,23,23,0.16), 0 2px 6px rgba(23,23,23,0.06)` | menus, popovers, the status menu |
| `--shadow-seg` | `0 1px 2px rgba(23,23,23,0.10), 0 0 0 0.5px rgba(23,23,23,0.06)` | the selected segment |
| `--shadow-panel` | `-16px 0 48px -24px rgba(23,23,23,0.18)` | the detail panel's left edge |

Shadows carry elevation, borders carry structure (`better-ui`). Keep borders on dividers, table rows,
inputs and selected states; drop them where they only faked depth. Every element with a shadow ring
also carries `border: 1px solid transparent`, so forced-colors mode — which strips every `box-shadow`
— still draws an edge.

On a backdrop page, a card takes **both** `--shadow-card` and a 1px `--color-line` border. Over a
photograph, a shadow alone does not separate a surface from its background.

**Changed from:** `--shadow-card` and `--shadow-menu` were tuned to pure black; both are retuned to
`#171717` and made slightly deeper, because they now have to work over a photograph.
`--shadow-panel` is new, for the same reason.

---

## 6. Layout

```
--rail-w:    72px     the dark left rail
--panel-w:   460px    the detail panel
--page-max:  1440px   content max-width inside the page shell
--row-h:     64px     a table row
--row-h-sm:  56px     a row inside the activity rail
--toolbar-h: 64px     the filter / search toolbar
```

### 6.1 The dark left rail

Replaces the translucent 232px sidebar. Full height, fixed, `--color-rail` `#171717`,
`--rail-w` 72px, `z-index: 30`, no shadow, no border, no blur.

- **Top:** app mark, 40px square, `--radius-md`, at `--space-4` from the top, centered.
- **Nav:** six icon buttons — Dashboard, Listings, Tracker, Coach, Profile, Add. 44px square,
  `--radius-md`, stacked with `--space-2`, centered. Icons 20px, `currentColor`, stroke 1.5
  (inactive) / 2 (active).
  - inactive glyph `--color-ink-4`, no fill
  - hover `--color-rail-hover` fill, glyph `#FFFFFF`
  - active `--color-rail-active` fill, glyph `#FFFFFF`, stroke 2, **plus** a 3px × 20px
    `#FFFFFF` marker on the rail's left edge at `--radius-full`. The fill alone is not enough of a
    state cue on a dark surface.
  - Every rail button has a `title` and an `aria-label`. An icon-only rail without labels is a
    usability debt we are accepting; the tooltip is the mitigation, and it is mandatory.
- **Bottom:** settings, then the API connectivity dot — 8px, `--color-online` / `--color-offline`,
  with an `aria-label` naming the state in words. Color is never the only channel.

**Changed from:** the 232px translucent sidebar is gone, with it the "Target roles" live-count list
and the host/API footer text. The role counts move to the dashboard as their own card (§6.4); the
API host string moves to the Profile page. See open question 1.

### 6.2 The page shell

```
body            height 100vh; overflow hidden; background var(--color-page)
.rail           fixed, 0 0 0 0, width var(--rail-w)
.backdrop       fixed, inset 0 0 0 var(--rail-w), z-index 0        (§3.1)
.page           margin-left var(--rail-w); position relative; z-index 1;
                height 100vh; display flex
.page-main      flex 1; min-width 0; overflow-y auto; overscroll-behavior contain
.page-inner     max-width var(--page-max); margin 0 auto;
                padding var(--space-10) var(--space-10) var(--space-12)
.page-panel     width var(--panel-w) (0 when closed); overflow-y auto;
                overscroll-behavior contain
```

The page itself never scrolls; the main column and the panel scroll independently. Desktop first; no
breakpoints below 1280px are specified and none are needed.

**Page header** sits inside `.page-inner`: `--text-title` title, `--text-lead` subtitle beneath it,
and the page's actions right-aligned on the title's baseline. `--space-8` below it.

### 6.3 Grids

**KPI row** (dashboard) — the Juney `05` structure exactly:

```
grid-template-columns: repeat(4, minmax(0, 1fr)) 320px;
gap: var(--space-4);
```

Four KPI cards, then `hero-card-dashboard` as the fifth cell at a fixed 320px.

**Dashboard body** — main column plus the activity rail:

```
grid-template-columns: minmax(0, 1fr) 340px;
gap: var(--space-6);
```

**Listings / Tracker** — one full-width `--radius-2xl` container card holding the toolbar, the header
row and the rows. No side rail.

### 6.4 The table row, at 64px

The row is a CSS grid, never a flex row, so columns line up across rows.

| | panel closed | panel open |
| --- | --- | --- |
| columns | `minmax(220px,1.1fr) minmax(0,2.4fr) 120px 112px 44px` | `minmax(160px,1fr) minmax(0,1.6fr) 0 112px 44px` |
| height | `--row-h` 64px | 64px |
| padding | `0 var(--space-4) 0 var(--space-6)` | same |

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

| variant | height | fill | text | border | hover |
| --- | --- | --- | --- | --- | --- |
| primary | 40px | `--color-ink` | `--color-ink-inverse` | transparent | `#000000` |
| secondary | 40px | `--color-track` | `--color-ink` | transparent | `rgba(23,23,23,0.10)` |
| outline | 40px | `--color-surface` | `--color-ink` | 1px `--color-line-strong` | `--color-hover` |
| ghost | 36px | none | `--color-ink-3` | none | `--color-hover` |
| icon | 36px sq | none | `--color-ink-3` | none | `--color-hover` |
| hero (on the image card) | 36px | `rgba(255,255,255,0.94)` | `--color-ink` | transparent | `#FFFFFF` |

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

| card | radius | padding | surface |
| --- | --- | --- | --- |
| container (table, chart) | `--radius-2xl` | `--space-3` around the inner surface | veil + border + `--shadow-card` |
| KPI | `--radius-xl` | `--space-5` | veil + border + `--shadow-card` |
| activity rail | `--radius-xl` | `--space-5` | veil + border + `--shadow-card` |
| hero image | `--radius-xl` | `--space-5` | the photograph (§7.11) |
| panel | `--radius-2xl` on its outer corners | — | opaque |

"veil" means `--color-surface-veil` + `backdrop-filter: blur(20px) saturate(1.05)`, falling back to
`--color-surface`.

### 7.10 KPI card

`--radius-xl`, `--space-5` padding, `--shadow-card`, minimum height 136px.

1. Label at `--text-label`, `--color-ink-3`.
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
`hero-card-dashboard`, `--scrim-image-card` as an `::after`, image outline per §3.3.

Content, bottom-aligned, `--space-5` padding:
- the count at `--text-display` in `--color-ink-inverse`
- one label at `--text-lead`/500 at `rgba(255,255,255,0.80)`
- up to two `hero` buttons in a row with `--space-2`

Minimum rendered size 320 × 180. Below that the text no longer clears the scrim's dark zone, and the
card must be replaced by an ordinary KPI card rather than shrunk.

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

### 7.15 Empty states

A real sentence at `--text-lead` on `--color-ink-2`, then one action that fills the screen. Centered
in its container, `--space-12` of vertical padding. Never seed sample rows to make a screen look
populated. Coach's empty state is the one that also carries the `coach-empty` image.

---

## 8. States

Every component defines all of these. A state that isn't listed doesn't exist.

| state | treatment |
| --- | --- |
| hover | rows `--color-row-hover`; controls `--color-hover`; rail `--color-rail-hover`. `--duration-hover` 100ms on `background-color` only. All hover styling lives under `@media (hover: hover)` — Tailwind 4's `hover:` already compiles there |
| pressed | `scale(0.96)` over `--duration-quick` with `ease-out`, only on onboarding role chips and primary buttons. Never on a disabled control: use `enabled:active:`. `-webkit-tap-highlight-color: transparent` wherever a control draws its own press |
| selected | row: `--color-selected` fill plus a 2px × 40px `--color-ink` marker at the row's left edge. Nav: §6.1. Segment: §7.6. Selection always has a shape cue, not only a fill |
| focus | `outline: none; box-shadow: 0 0 0 3px var(--color-ring)` plus `border-color: var(--color-ink)`. Applied via `:focus-visible` globally. On the dark rail the ring is `rgba(255,255,255,0.45)` instead — specify it on the rail, don't let the global rule disappear into the dark |
| loading | a `--color-tile` block at the element's exact final size and radius, pulsing opacity 1 → 0.6 → 1 over 1200ms `ease-in-out`. Never a spinner inside a row. Never a layout that reflows when data lands: the skeleton is the same height as the row |
| empty | §7.15 |
| error | an inline strip at the top of the affected card: `rgba(179,38,30,0.08)` fill, `#B3261E` text at `--text-body`, a 16px warning glyph, `--radius-md`, entering with `--animate-in`. Never a toast, never a modal. The sentence says what failed and what to do |
| disabled | `opacity: 0.45`, `cursor: not-allowed`, no hover, no press, no focus ring on a non-focusable element |
| offline | the rail dot turns `--color-offline` and its `aria-label` changes to "API offline". Nothing else in the UI changes color |

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
- `--duration-standard` `300ms` — the detail panel's width, and *(new)* the backdrop's fade-in
- `--default-transition-duration` is `--duration-quick`, so a bare `transition-*` is 150ms and only
  the off-default tiers name a duration

**Entrance pattern** — one recipe, 150ms, opacity with `translateY(4px)` and `scale(0.98)`.
- `--animate-pop` enters downward from its trigger: menus and popovers
- `--animate-in` enters upward: inline inputs, empty states, a save confirmation, an error strip
- Nothing else animates in. **Rows never stagger or fade.** A table of 4,000 rows that animates on
  every load or filter change is noise, not polish. This does not change at 64px rows — bigger rows
  make a stagger worse, not better.

**The backdrop fade (new).** The only motion the imagery is allowed. `.backdrop-img` starts at
`opacity: 0` and transitions to `1` over `--duration-standard` with `--ease-brand` on its `load`
event. Opacity only — no scale, no blur animation, nothing that moves. It runs once per page mount
and is skipped entirely under reduced motion.

**Other rules**
- Press is `scale(0.96)` over `--duration-quick`, gated behind `motion-safe:`, on onboarding role
  chips and primary buttons only. A disabled control never scales.
- Exits are instant. Menus, the panel and empty states unmount without motion, which carries no
  information here.
- Route changes are instant. No page transition — including when the backdrop changes between pages.
  The new backdrop fades in on its own load; the page does not cross-fade.
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
  button is in the DOM at all times and only its *opacity* is hover-dependent, so it is always
  reachable by keyboard.
- **Reduced motion:** the global `prefers-reduced-motion: reduce` block stays. Under it, the backdrop
  image appears without a fade, the press scale does not run, and the loading pulse holds at a
  constant `--color-tile`.
- **Color is never the only channel.** Status pills carry a label beside the dot. Delta chips carry
  an arrow. The connectivity dot carries an `aria-label`. The active rail item carries a shape marker
  as well as a fill.
- **Images:** every decorative image is `alt=""` and `aria-hidden="true"`. The sparkline is
  `aria-hidden`; its value is already in the KPI number beside it.
- **Forced colors:** every shadow ring has a transparent border beneath it (§5.3). Backdrops and
  scrims disappear in forced-colors mode and the page must still be correct — which it is, because
  nothing readable was on them.

---

## 11. Screens

1. **Dashboard** (`/`) — `backdrop-dashboard`. KPI row of four cards plus `hero-card-dashboard`; then
   a two-column body: the 28-day chart and "Top of your board" on the left, the activity rail and the
   target-roles card on the right; then "Your applications".
2. **Detail panel** — the same screen with a row selected, the panel open at 460px.
3. **All listings** (`/listings`) — `backdrop-listings`. One `--radius-2xl` container card holding the
   filter toolbar, the header row, 64px rows and "Load more".
4. **Tracker** (`/tracker`) — `backdrop-tracker`. The segmented control above the container card,
   rows grouped under sticky status headers. Tracking is separate from browsing; never merge them
   back.
5. **Coach** (`/chat`) — `backdrop-coach`. A placeholder card with `coach-empty` and a sentence saying
   it is a later phase.
6. **Profile** (`/profile`) — `backdrop-profile`. A profile card topped by `profile-cover`, then the
   saved profile fields and the API host line.
7. **Onboarding** (`/onboarding`) — `backdrop-onboarding`. Title at `--text-title-lg`, the role chips,
   and the "Other" chip.

---

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
- No text on a photograph outside §7.11 and §7.12.
- No card below `--color-surface-veil`'s 0.92 opacity.
- No glassmorphism on cards beyond the specified 20px `backdrop-filter`, no neon, no heavy shadows.
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
2. **The `new` status pill's color.** Blue left the palette and orange is reserved. *Provisional:*
   `new` becomes a neutral off-black pill, and the accent is spent on the *count* of new listings in
   the KPI row. The cost is that a new row no longer announces itself in the table by color — it still
   has the unread dot.
3. **`saved` sits near the accent.** `#FF9500` amber and `#FF4E02` orange are neighbours.
   *Provisional:* keep `saved` at its current amber, used only as a 13%-opacity tint and never as a
   solid fill, so the two never compete as solids. If they still read as the same thing on screen,
   `saved` should move to a yellow-green rather than the accent moving.
4. ~~**Nine image slots is a lot of approvals.**~~ **Decided: generate two.**
   `backdrop-dashboard` and `hero-card-dashboard` are commissioned; the other seven ship on their
   fallback gradients until they earn a render. Build against the fallbacks regardless — a slot whose
   image never arrives has to look deliberate, which is the whole point of specifying them.
5. **The sparkline has no data source.** §7.10 specifies one because the reference has one, but
   nothing in the API returns a per-KPI time series today. *Provisional:* ship KPI cards without
   sparklines and add them when there is real data. Do not fake the curve — §14.
6. **The activity rail has no data source either.** There is no event log in the API. *Provisional:*
   on the dashboard, the right column holds the target-roles card and "Your applications" instead,
   and the activity rail stays specified here for when an event log exists.
7. **Reduced transparency.** `prefers-reduced-transparency` is not handled anywhere in this document.
   *Provisional:* if it is set, drop the backdrop image entirely and use the fallback gradient with
   fully opaque surfaces. Cheap to do, and worth doing in the implementation task.
