# PLAN.md

Build order, with a `done means` line per phase. The verifier agent reads the
current phase, runs the exact command on that line, and compares real output to
the criteria.

**Current phase: 2 — role variants and The Muse**

## The app is role-first

The user manages **role title variants**, never companies. Every primary source
is queried by those variants. Company job boards are an internal implementation
detail: the app discovers them on its own and the user never sees or edits a
company list.

Role variants live in `roles.txt`, one variant per line — the single user-facing
targeting setting (e.g. `software engineering intern`, `swe intern`,
`data science intern`). This replaces `companies.txt`, which is removed.

## Sources

### Primary — queried by role title variants

1. **The Muse API** — free key, filter `level=Internship` / `Entry Level`,
   multi-industry, full descriptions. `full_text=True`.
2. **Adzuna** — free ~1,000 calls/month, descriptions are truncated, requires
   "Jobs by Adzuna" attribution. Discovery only, `full_text=False`.
3. **USAJobs** — free key, User-Agent must be my registered email, federal only.
4. **Gmail LinkedIn alerts** (later) — Gmail API, read-only scope, reads LinkedIn
   job alert emails, extracts title/company/location/url, `full_text=False`.
   **LinkedIn: no scraping, ever.**

### Internal — ATS boards, never user-managed

**Greenhouse / Lever / Ashby** public board endpoints. No key, full text.

- Discovered slugs are stored in an `ats_boards` table.
- A slug is **auto-added** whenever any listing's url points at
  `greenhouse.io`, `lever.co`, or `ashbyhq.com` — so every primary source feeds
  board discovery as a side effect of normal collection.
- Seeded **once** from Simplify's public internship repo. The exact repo and
  file to read are confirmed at implementation time, not guessed here.
- Each known board is pulled, and only listings whose **titles match the user's
  role variants** are kept. A board carries thousands of unrelated roles, so the
  title filter is what makes pulling it affordable.
- Poll every few hours max. Lever: try `api.lever.co`, then `api.eu.lever.co`.

Later: a "save this job" bookmarklet that posts the current page to the local
server, and an optional JSearch source using my own key.

## Design rules

- Each source = one plain function returning the same dict shape:
  `title, company, location, url, description, posted_at, source, full_text` (bool).
- Only listings with `full_text=True` go to skill extraction.
- Track API calls per source in the DB and stop before limits.
- Prompts live in `prompts/*.txt`. Log every LLM call (input, output, tokens,
  cost) to the DB.

## Workflow

- ruff (lint + format) and pre-commit. A GitHub Actions workflow running ruff
  and pytest on every push and PR.
- One branch per phase, open a PR with gh, wait for CI to pass, then merge.
  Explain each git/gh step in one sentence.
- Save one real response per source to `tests/fixtures/`. Tests and evals use
  fixtures, never live APIs.
- `evals/` holds labeled data; `evals/run.py` prints metrics. Log results in
  README.
- Before every commit, run the reviewer agent on the diff, then the verifier
  agent on the current task. Fix all FAIL items before committing.
- Turn on GitHub secret scanning + push protection after the repo is created.

## Phases

The primary sources come first, because each one feeds the `ats_boards` table.
By the time the ATS phase runs, discovery has already found real boards, so the
seed is a backstop rather than the only input.

### Phase 0 — scaffold — COMPLETE
Repo, ruff, pre-commit, CI, CLAUDE.md, reviewer subagent, source contract.
**done means:** `ruff check . && ruff format --check . && pytest` passes and
`intern-app config` prints the resolved settings.

### Phase 1 — storage — COMPLETE
SQLite schema, upserts, `api_calls` quota accounting, `llm_calls` cost log.
**done means:** `pytest tests/test_db.py tests/test_quota.py tests/test_pricing.py`
passes and `intern-app status` prints listings, quota left, and LLM spend.

### Phase 2 — role variants and The Muse
`roles.txt` loading and title matching; `sources/muse.py` as one function
querying each role variant, internship and entry-level filters, full
descriptions, quota-checked, `full_text=True`.
**done means:** `pytest tests/test_roles.py tests/test_muse.py` passes against
`tests/fixtures/muse_search.json`, and `intern-app fetch --source muse --offline`
prints normalized listings parsed from that fixture with no network call.

### Phase 3 — Adzuna
Queried by role variants. Discovery only, `full_text=False`, "Jobs by Adzuna"
attribution carried on every listing, tightest quota accounting.
**done means:** `pytest tests/test_adzuna.py` passes and asserts every returned
listing has `full_text=False`, an empty description, and the attribution string.

### Phase 4 — USAJobs
Queried by role variants. Federal only, `User-Agent` set to the registered email
from `USAJOBS_EMAIL`.
**done means:** `pytest tests/test_usajobs.py` passes and asserts the request
carries the registered email as User-Agent and the API key is never logged.

### Phase 5 — ATS board discovery and pulling
`ats_boards` table; a slug is auto-added from any listing url on greenhouse.io,
lever.co, or ashbyhq.com; a one-time seed from Simplify's public internship repo;
per-board pull filtered to role-variant title matches; Lever EU fallback; 3-hour
poll floor.
**done means:** `pytest tests/test_ats.py` passes, including a test that a
greenhouse.io listing url auto-adds its slug, that a board pull drops titles not
matching any role variant, and that the Lever EU fallback fires when the US host
404s.

### Phase 6 — Gmail LinkedIn alerts
Gmail API, read-only scope, parse alert emails to title/company/location/url,
`full_text=False`.
**done means:** `pytest tests/test_gmail.py` passes against a saved alert email
fixture and asserts `full_text=False` and that no message body is stored.

### Phase 7 — skill extraction and evals
`prompts/extract_skills.txt`, Claude call via structured outputs, every call
logged to `llm_calls` with tokens and cost. `evals/run.py` prints metrics.
**done means:** `pytest tests/test_extract.py && python evals/run.py` passes and
prints precision/recall against the labeled set, with results logged in README.

### Phase 8 — profile and ranking
My profile, skill matching, a score per listing.
**done means:** `pytest tests/test_rank.py && intern-app rank --offline` prints
listings in score order with the matched and missing skills per listing.

### Phase 9 — dashboard
FastAPI + HTML, filterable ranked list, applied/saved state, Adzuna attribution
visible.
**done means:** `pytest tests/test_server.py` passes and `intern-app serve`
answers `GET /` with 200 and renders the ranked list.

### Phase 10 — later
"Save this job" bookmarklet posting to the local server; optional JSearch source
using my own key.
**done means:** deferred until phase 9 is merged.
