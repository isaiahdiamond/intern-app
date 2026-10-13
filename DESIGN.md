# DESIGN.md

Source of truth for how intern-app looks and feels. Read this before building or changing any UI.
Don't invent colors, sizes or components that aren't here. If something is missing, ask.

This document describes the design Claude produced in `design/system/Intern App.dc.html`, which
replaced the earlier design language. Where this file and that one disagree, the `.dc.html` wins
and this file should be corrected. `design/system/Intern App Screens.dc.html` shows the five
screens at 1440x900. `design/system/references/` holds the screenshots that inspired it; they are
context only.

## Feel

A calm, light, Mac-quality desktop tool. Dense where you work (tables), roomy where you decide
(onboarding, the detail panel). Mostly neutrals, one bright blue, very little decoration.

- System font, tight and crisp
- Soft rounded corners, hairline borders, one soft shadow on dashboard cards
- Translucent sidebar with heavy background blur
- Segmented controls instead of tab bars
- Large bold page titles with a mono date beside them
- Short, smooth motion

## Stack

React + Vite + TypeScript, Tailwind CSS v4. Backend is Python on `localhost:8000`; Vite proxies
`/api` to it. No component library: the design is specific enough that plain elements are clearer
than restyled primitives. Icons are inline SVG paths from `src/lib/icons.ts` — the design specifies
each path, so there is no icon package.

## Color

Base
- `--color-bg` `#F5F5F7` page background
- `--color-surface` `#FFFFFF` cards, tables, the detail panel
- `--color-sidebar` `rgba(232,232,237,0.62)` with `blur(40px) saturate(180%)` and
  `inset -1px 0 0 rgba(255,255,255,0.6)`
- `--color-head` `#F7F7F9` dashboard table headers and legend rows
- `--color-head-2` `#FAFAFB` list and tracker table headers, group headers
- `--color-tile` `#EDEDF0` company icon tile, empty chart bars

Lines (all hairline, 1px)
- `--color-line` `rgba(0,0,0,0.08)` card and control borders
- `--color-line-soft` `rgba(0,0,0,0.06)` dashboard card borders, dividers
- `--color-line-row` `rgba(0,0,0,0.05)` between table rows
- `--color-line-strong` `rgba(0,0,0,0.1)` menus, secondary buttons

Fills
- `--color-hover` `rgba(0,0,0,0.04)` sidebar hover
- `--color-row-hover` `rgba(0,0,0,0.025)` list and tracker row hover
  (dashboard rows hover to `#FAFAFC`)
- `--color-selected` `rgba(10,132,255,0.07)` the selected row
- `--color-track` `rgba(118,118,128,0.12)` segmented control track, secondary button

Text
- `--color-text` `#1D1D1F`
- `--color-text-2` `#3A3A3C` mono data, dense values
- `--color-text-3` `#6E6E73` secondary
- `--color-text-4` `#86868B` labels, timestamps, placeholders
- `--color-text-5` `#8E8E93` uppercase column headers

Accent
- `--color-accent` `#0A84FF` primary fill, active nav, unread dot, focus ring
- `--color-accent-hover` `#0077ED`
- `--color-accent-text` `#0066CC` blue text and links
- Active nav item: `rgba(10,132,255,0.13)` fill with `#0066CC` text at weight 600
- Focus ring: `0 0 0 3px rgba(10,132,255,0.18)`

Status (pills, dots, the donut, the tracker group headers)

| key | label | text | background | dot |
| --- | --- | --- | --- | --- |
| `new` | New | `#0066CC` | `rgba(10,132,255,0.10)` | `#0A84FF` |
| `saved` | Saved | `#9A5400` | `rgba(255,149,0,0.13)` | `#FF9500` |
| `applied` | Applied | `#1E7A34` | `rgba(52,199,89,0.14)` | `#34C759` |
| `interviewing` | Interviewing | `#7A3DA8` | `rgba(175,82,222,0.12)` | `#AF52DE` |
| `offer` | Offer | `#0B6E80` | `rgba(48,176,199,0.15)` | `#30B0C7` |
| `rejected` | Rejected | `#6E6E73` | `rgba(0,0,0,0.05)` | `#AEAEB2` |
| `hidden` | Archived | `#8E8E93` | `rgba(0,0,0,0.04)` | `#C7C7CC` |

These keys are the backend's, not the design's: the design called `saved` "Interested". Use the
backend keys everywhere, since they are what `POST /api/status` accepts.

`hidden` takes a listing off both the board and the tracker, so it is not one of the statuses the
status menu offers — it is only ever reached through Archive, and is in the table because a stored
`hidden` row still turns up in Search and has to be drawn as something. A status key the table does
not know is drawn grey and labelled Unknown, never as New.

Status of the backend
- `--color-online` `#34C759` the sidebar's api-connected dot
- `--color-offline` `#FF3B30` the same dot when `/api/filters` cannot be reached

Gradient
- One blue glow at the top of the main column and the onboarding page, nowhere else:
  `radial-gradient(ellipse 70% 300px at 50% -40px, rgba(10,132,255,0.11), rgba(10,132,255,0.04) 45%, rgba(10,132,255,0) 100%)`

## Type

- UI: `-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", system-ui, sans-serif`
- Display (big numbers, card titles): the same stack led by `SF Pro Display`
- Mono: `ui-monospace, "SF Mono", Menlo, monospace` — counts, dates, ids, tags, URLs, status lines

Body default is 13px / 1.35 / `-0.005em`.

| use | size | weight | tracking |
| --- | --- | --- | --- |
| Page title | 28px | 600 | -0.022em |
| Onboarding title | 34px | 600 | -0.025em |
| Stat number | 34px | 600 | -0.035em, tabular-nums |
| Panel title | 20px | 600 | -0.018em |
| Card title | 15px | 600 | -0.012em |
| Row company (dashboard) | 13.5px | 600 | -0.01em |
| Row role / company | 13px | 500, 600 when unread | — |
| Controls, filters, menu items | 12.5px | 500 | — |
| Small labels, meta | 11.5px | 500/600 | — |
| Column headers (dashboard) | 11px | 600 | 0.04em, uppercase |
| Mono data | 10.5–12px | 400/500 | — |

Never above 600. Uppercase only on dashboard column headers.

## Shape and depth

- Radius: 5–7px tags and small buttons, 8px controls and filters, 9px segments and sidebar nav,
  10px menus and icon tiles, 11–13px status pills, 12px list cards, 16px dashboard cards,
  18px onboarding chips
- `--shadow-card` `0 1px 2px rgba(0,0,0,0.04), 0 8px 24px -12px rgba(0,0,0,0.08)` — dashboard cards
- `--shadow-menu` `0 10px 30px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.05)` — every popover
- `--shadow-seg` `0 1px 2px rgba(0,0,0,0.1), 0 0 0 0.5px rgba(0,0,0,0.06)` — selected segment
- The list and tracker cards have a border and no shadow

## Layout

- Sidebar 232px, translucent, full height: logo row 52px, nav, "Target roles" with live counts,
  footer with API state and host
- Main column: header at `30px 32px 0`, then the scroll area at `22px 32px 40px`
  (`4px` top on the tracker, whose segmented control sits above it)
- Right detail panel 420px, a flex sibling that animates its width
  `300ms cubic-bezier(0.32,0.72,0,1)`; the tables narrow their columns when it is open
- Desktop first. The page itself never scrolls; the main column and the panel scroll separately

## Components

Table row — the core of the app. A CSS grid, never a flex row, so columns line up across rows.

- List and tracker: 48px tall, `0 14px 0 30px`, columns
  `minmax(140px,1fr) minmax(0,2.2fr) 72px <action>`; with the panel open
  `minmax(0,1fr) minmax(0,1.4fr) 56px <action>`
- Dashboard: 62px tall, 34px icon tile, bolder company name
- Unread dot: 6px `#0A84FF`, absolutely placed 12px (dashboard 15px) from the left edge
- Company cell: icon tile, then company over location, both truncating
- Role cell: `display_title` at 13px, then the title tags; `title` is the tooltip
- Row hover `--color-row-hover`, selected `--color-selected`, top border `--color-line-row`

Company icon tile
- 28px / radius 7px in lists, 34px / radius 9px on the dashboard, 40px / radius 10px in the panel
- `--color-tile` background with a centred 🏢, which shows through whenever there is no icon
- The apply URL is a job board, not the company, so the domain is resolved separately and the icon
  is cached server-side. The page loads it from our own origin at `/api/icon/{company}`: the
  browser must never request an icon from a third party, because that would tell a logo service
  which companies are on the board
- `has_icon` on the row says whether one exists. Only request an icon when it does, and never
  render a broken image.

Title tags
- The row shows `level`, `education`, `term`, `citizenship` and years of experience as separate
  tags, in that order, and nothing when they are empty
- The first three come from the title, the last two only from the posting body, so a listing whose
  full text we never collected shows three tags at most and must still look right
- `citizenship` reads "US citizens", "Clearance" or "No sponsorship"; years reads "2+ yrs". These
  are knockout facts, which is why they sit on the row and not only in the panel
- Keep every label inside 15 characters. The tags share a `minmax(0,2.2fr)` column with a
  truncating `display_title`, and a long one eats the title instead of wrapping
- 18px tall, radius 5px, `rgba(0,0,0,0.035)` on a `--color-line-soft` border, 10.5px mono

Status pill
- 22px tall, radius 11px, 12px / 500, a 6px dot then the label, colors from the table above
- 108px fixed width in table columns so the column lines up; auto width in the panel
- A chevron at the right when it opens a menu

Menus (status, filters)
- 176px (status) or 232px (filters), 5px padding, radius 10px, `--color-line-strong` border,
  `--shadow-menu`, `pop 140ms ease-out`
- Items 28–30px, radius 6px, 12.5px, hover `rgba(10,132,255,0.08–0.10)`
- Status items: dot, label, blue check on the current one
- Filter items: 14px checkbox, label, mono count
- Clicking the page background closes them; the menu itself stops propagation

Filter chip
- 30px tall, radius 8px, white on a `--color-line-strong` border; active is
  `rgba(10,132,255,0.08)` on `rgba(10,132,255,0.35)` with `#0066CC` text
- Label in 500, the chosen value beside it in 400, then a chevron that flips when open
- A filter that cannot apply in the current mode is dimmed to 0.45 and does not open

Segmented control (tracker)
- `--color-track` track, 2px padding, radius 9px; segments 26px, radius 7px, 12.5px / 500
- Selected: white with `--shadow-seg`; the count beside each label is mono 11px

Search input
- 30px, radius 8px, magnifier at 14px, 12.5px text. White with a `--color-line` border in the
  tracker toolbar; `--color-bg` with a `--color-line-soft` border inside the listings card

Dashboard stat card
- Radius 16px, `--shadow-card`, 20px padding; label, then the number at 34px, then a 22px delta
  chip; a 36px tinted icon tile pinned at `top:16px right:16px`
- Delta chip is green `rgba(52,199,89,0.12)` / `#1E7A34` when positive, otherwise
  `rgba(0,0,0,0.045)` / `#6E6E73`

Charts
- Bar chart: 170px tall, 5px gaps, bars max 16px wide, radius `5px 5px 2px 2px`, blue
  `rgba(10,132,255,0.55)`, empty days a 3px `--color-tile` stub; horizontal rules via
  `repeating-linear-gradient` every 42px; the count sits above each bar in mono
- Donut: a 156px `conic-gradient` of the status dots with a white 20px-inset hole holding the
  total; `--color-tile` when there is nothing to show. Legend rows are 34px on `--color-head`

Detail panel
- 52px header: position text in mono, then prev / next / close as 28px ghost buttons
- Body: icon tile, title, company, then a primary "Open posting" and a secondary next-status button
- Properties: a 104px label column, a 14px icon, then the value; status and link are the last two
- Everything in it comes from the listing row. There is no description or parsed-requirement data
  in the API yet, so the panel says so plainly rather than showing an empty section

Buttons
- Primary: `--color-accent` fill, white, 30px, radius 8px, 13px / 500
- Secondary: `--color-track` fill, no border, same size
- Outline: white on `--color-line-strong`, used for "Listing" and "Load more"
- Ghost: no fill, `--color-text-3`, hover `rgba(0,0,0,0.05)`
- One primary per screen

Onboarding role chips
- 36px tall, radius 18px, 14px / 500, white on `--color-line-strong`; selected is
  `#0A84FF` fill with white text; `scale(0.97)` while pressed
- "Other" is a dashed-border chip that becomes an inline input with an "Add" button

Empty states
- A real sentence about why the screen is empty and one action that fills it. Never seed sample
  rows to make a screen look populated.

## Motion

- 120–180ms on hovers and fills; 300ms `cubic-bezier(0.32,0.72,0,1)` on the panel width
- `pop 140ms ease-out` on menus, `in 160ms ease-out` on inline inputs
- No bouncing, no loops, respect `prefers-reduced-motion`

## Screens

1. **Dashboard** (`/`) — four stat cards, the 28-day applications chart and the status donut, then
   "Top of your board" (the ranked new listings) and "Your applications" (the tracker).
2. **Detail panel** — the same dashboard with a row selected.
3. **All listings** (`/listings`) — the filter bar, the table, "Load more".
4. **Tracker** (`/tracker`) — its own tab. Segmented control by status, rows grouped under
   collapsible status headers. Tracking is separate from browsing; never merge them back.
5. **Onboarding: role picker** (`/onboarding`) — the chips, reachable from "Edit" in the sidebar.

Coach (`/chat`) and Profile (`/profile`) stay in the nav. Coach is a later phase and says so.

## Data rules

- Render `display_title`, never `title`. `title` keeps the season, team and degree; it belongs in
  the tooltip and in the panel's "Raw posting title".
- `posted_at`, `level`, `education`, `term` and `industry` can all be empty. Every row must look
  right with none of them set.
- `location` can be hundreds of characters. Truncate it in rows; wrap it in the panel.
- `industry_rank` is 1-based preference and `999` means unranked — show "unranked", not 999.
- `copies` above 1 means duplicate postings were collapsed; say so in the panel.
- `full_text` is 0 for almost everything, which the panel reports as "link only".

## Attribution

Adzuna rows must carry "Jobs by Adzuna" wherever they surface: a mono line under any table that
contains one, and beside the Source property in the panel.

## Don't

- No dark mode for now
- No gradient other than the one top glow
- No heavy shadows, no glassmorphism on cards, no neon
- No company logos; the icon tile stays small and neutral
- No emoji in the UI except the icon-tile fallback
- No invented values. If the design asks for something the API does not have — salary, logos,
  deadlines, skill matches — leave it out and say why, rather than filling it with a placeholder.
