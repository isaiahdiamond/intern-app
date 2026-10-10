# DESIGN.md

Source of truth for how intern-app looks and feels. Read this before building or changing any UI. Don't invent colors, sizes or components that aren't here. If something is missing, ask.

## Feel

A calm, light, Mac-quality desktop tool. Think Linear's structure with Apple's finish: dense where you work (lists, tables), roomy where you decide (onboarding, skill gaps). Mostly neutrals, one bright blue, very little decoration.

Apple influences to keep:
- System font (SF Pro on Mac), tight and crisp
- Soft rounded corners, hairline borders, almost no shadows
- Translucent sidebar with background blur
- Segmented controls instead of tab bars
- Large bold page titles
- Short, smooth motion

## Stack

React + Vite + TypeScript, Tailwind CSS v4, shadcn/ui (Radix primitives), lucide-react icons. Backend is Python, served on localhost.

## Color

Base
- `--bg` `#F5F5F7` page background (Apple off-white)
- `--surface` `#FFFFFF` cards, list, panels
- `--sidebar` `rgba(245,245,247,0.72)` with `backdrop-filter: blur(20px) saturate(180%)`
- `--border` `rgba(0,0,0,0.08)` hairline, 1px
- `--hover` `rgba(0,0,0,0.04)`
- `--selected` `rgba(10,132,255,0.10)`

Text
- `--text` `#1D1D1F`
- `--text-2` `#6E6E73` secondary
- `--text-3` `#86868B` labels, timestamps, placeholders

Accent (blue)
- `--accent` `#0A84FF` primary buttons, active nav, focus ring, "New" status
- `--accent-hover` `#0077ED`
- `--accent-text` `#0066CC` blue text and links on light backgrounds (`#0A84FF` is too light for small text)
- Focus ring: `0 0 0 3px rgba(10,132,255,0.30)`

Status (muted, used only in status pills)
- New: text `#0066CC`, bg `rgba(10,132,255,0.10)`
- Interested: text `#B25000`, bg `rgba(255,149,0,0.12)`
- Applied: text `#1F7A3A`, bg `rgba(52,199,89,0.12)`
- Rejected: text `#6E6E73`, bg `rgba(0,0,0,0.05)`

Gradient
- One faint blue glow at the top of the main content area only:
  `background: radial-gradient(1200px 360px at 50% -120px, rgba(10,132,255,0.08), transparent 70%), #F5F5F7;`
- Never on cards, buttons, text or the sidebar. If you can clearly see it, it's too strong.

Roughly 90% of any screen should be neutrals. Blue is for action and attention only.

## Type

- UI font: `-apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter", system-ui, sans-serif`
- Mono: `ui-monospace, "SF Mono", "Geist Mono", "JetBrains Mono", monospace`
- Mono is only for agent/data bits: counts, timestamps, skill tags, activity chips

Scale
- Page title: 28px / 600 / tracking -0.02em
- Section title: 17px / 600
- Body and rows: 13px / 400, line height 1.45
- Small labels: 12px / 500, `--text-3`
- Mono data: 12px / 500

Never use weights above 600. No all-caps except tiny group labels (11px, 500, tracking 0.04em).

## Spacing and shape

- 4px grid: 4, 8, 12, 16, 20, 24, 32, 48
- Radius: 6px small (pills, tags), 10px controls (buttons, inputs, favicons), 14px cards and panels
- Shadows: none by default. Popovers and the detail panel only: `0 8px 30px rgba(0,0,0,0.08)`
- Row height in lists: 40px

## Layout

- Left sidebar 232px, translucent, fixed: app name, nav (Dashboard, Search, Chat, Profile), saved searches below
- Main content: max width 1200px, 32px padding, large page title at top
- Right detail panel 420px, slides in over the list when a row is selected, closes on Esc
- Desktop first; must still work down to 1024px wide

## Components

Listing row (the core of the app)
- Left: company favicon 24px, radius 6px, 1px `--border`
- Then: role title (13px, 500, `--text`), below it `Company · Location` (12px, `--text-2`)
- Right side: up to 3 skill tags (mono, 12px, `--hover` bg, radius 6px), posted date (mono, `--text-3`), status pill
- Hover: `--hover` background. Selected: `--selected` background
- Rows grouped by status with a group header: label + count in mono, e.g. `New 12`

Company favicon
- Loaded from the backend's local cache, never fetched from the browser directly
- Missing icon: same 24px rounded square, `--hover` background, centered neutral emoji 🏢 at 14px
- Never show a broken image or an empty box

Status pill
- 22px tall, radius 6px, 12px / 500, colors from Status above
- Click opens a small menu to change status

Agent activity chips
- Small mono chips that show what the agent did: `found 12 new listings`, `parsed 340 requirements`, `3 match your roles`
- White surface, 1px border, radius 8px, 12px mono, small lucide icon on the left in `--text-3`
- Shown in a row under the dashboard title, newest first, max 3 visible

Buttons
- Primary: `--accent` fill, white text, 13px / 500, 32px tall, radius 10px
- Secondary: white fill, 1px border, `--text`
- Ghost: no border, `--text-2`, hover `--hover`
- One primary button per screen

Segmented control
- Use for view switches (All / New / Interested / Applied). Apple style: `--hover` track, white selected segment with subtle shadow, radius 8px

Inputs
- 32px tall, white, 1px border, radius 10px, focus ring as above
- Search: magnifier icon left, `⌘K` hint right in mono

Onboarding role chips
- Pill chips, 32px tall, radius 999px, white with border. Selected: `--accent` fill, white text
- "Other" chip opens a text input

Cards
- `--surface`, 1px border, radius 14px, 20px padding, no shadow

## Motion

- 150–200ms, `cubic-bezier(0.2, 0.8, 0.2, 1)`
- Detail panel slides in from the right; menus fade and scale from 0.98
- No bouncing, no looping animations, respect `prefers-reduced-motion`

## Don't

- No dark mode for now
- No gradients other than the one top glow
- No heavy shadows, glassmorphism on cards, or neon
- No big company logos or logo cards; favicons stay small
- No progress steppers for application stages
- No emoji in the UI except the favicon fallback
- No default shadcn look left untouched: apply these tokens to every component
