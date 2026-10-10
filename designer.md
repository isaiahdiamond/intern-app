# Agent prompts for the MVP UI

Run these in order in Claude Code, one per session or after the previous one is working. Review the result in the browser before moving on.

## 0. Add to CLAUDE.md (once)

```
## Design
DESIGN.md is the source of truth for all UI. Read it before creating or changing any frontend file. Use its tokens and components exactly; don't invent new colors, sizes or styles. If something isn't covered, ask me.

## Code style
Write code for a human beginner to read. Simple, flat, procedural. Function components only, no classes, no custom hooks or abstraction layers unless I ask. Short names. No comments that explain what code does. No try/catch except around network and file I/O. Use built-ins over custom helpers. No placeholder tests or boilerplate.
```

## 1. Scaffold, tokens and app shell

```
Read DESIGN.md first.

Set up the frontend in /web: React + Vite + TypeScript, Tailwind CSS v4, shadcn/ui, lucide-react.

1. Put every token from DESIGN.md (colors, fonts, radii, shadow, motion) into the Tailwind theme as CSS variables in one file. Restyle the shadcn Button, Input, DropdownMenu and Tabs to match DESIGN.md.
2. Build the app shell: translucent left sidebar (Dashboard, Search, Chat, Profile, then a "Saved searches" group), main area with the faint top blue glow, large page title.
3. Empty placeholder pages for each nav item, routed with react-router.

Keep it minimal. Show me the shell running before adding anything else.
```

## 2. Listings board (dashboard)

```
Read DESIGN.md first, especially "Listing row", "Company favicon", "Status pill" and "Agent activity chips".

Build the Dashboard page with mock data (30 listings in a local JSON file; real companies, roles, locations, 2-4 skill tags each, a domain field, mixed statuses).

- Title "Dashboard", then a row of 3 agent activity chips
- Segmented control: All / New / Interested / Applied / Rejected
- Search input with ⌘K hint
- List grouped by status with group headers showing counts in mono
- Rows exactly as described in DESIGN.md, 40px tall
- Clicking a status pill opens a menu to change it (local state is fine for now)
- Clicking a row opens the right detail panel: favicon, role, company, a properties block (label left, value right: location, posted, source, status, link), then the parsed requirements as tags. Esc closes it.

For favicons use a FavIcon component that takes a domain, loads /api/favicons/<domain>, and shows the 🏢 fallback on any error or missing domain. Never render a broken image.
```

## 3. Favicon cache (backend)

```
Add favicon caching to the Python backend.

- For each listing, the parse step should return the company's own website domain (e.g. "stripe.com"), not the apply URL's domain (greenhouse.io, lever.co, myworkdayjobs.com and similar are not company domains).
- On new listings, for each domain not already cached, download https://www.google.com/s2/favicons?domain=<domain>&sz=64 once and save it to data/favicons/<domain>.png.
- If the request fails or returns Google's generic default globe (check status and image size), record it as a miss in a small JSON file so we don't retry it every run. Retry misses after 30 days.
- Serve GET /api/favicons/<domain>: the cached file, or 404 if missing so the frontend shows the fallback.
- The frontend never calls Google directly.
```

## 4. Onboarding (after the board works)

```
Read DESIGN.md first, especially "Onboarding role chips".

Build first-run onboarding as a centered single column (max 560px) on the glow background, one question per step, with a thin progress bar at top and Back / Continue buttons:
1. School
2. Major
3. Role chips for that major (pre-made list), with an "Other" chip that shows a text input
4. Industries (chips)
5. Summary card, then "Start finding jobs" (primary button)

Use larger spacing than the dashboard: this screen should feel roomy and calm. Smooth fade between steps per the Motion section.
```
