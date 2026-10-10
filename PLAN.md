# PLAN.md

Scope right now: **tech roles, one user (me).** Get it working for me first.

**Current phase: 2 — Fetch and store for my roles**

Already built: repo, ruff, pre-commit, CI, the reviewer and verifier agents, the
source contract (`sources/base.py`), the SQLite layer (`listings`, `api_calls`
quota accounting, `llm_calls` cost log), and **phase 1 onboarding** — the
four-question form, `profile` / `profile_roles` / `profile_industries`, the role
chips, and the LLM-backed Other button.

## What the user sees

**Onboarding, one time** (editable later in Profile):

1. School
2. Major
3. Roles — multiple-choice chips of the most common roles for that major, most
   popular first; select several. An **Other** button asks the LLM what you're
   looking for and turns the answer into 4-8 new chips to select.
4. Industries of interest, multi-select and **ranked** — the order matters.

Then straight to the Dashboard.

**Dashboard tab** — new jobs matching my roles, ordered by my industry
preference; a tracker with status (`saved` / `applied` / `interviewing` /
`rejected` / `offer`) and history; an industry filter.

Industries **order** what surfaces, they do not exclude. A listing in a
low-preference industry still appears, just further down, and one with no
industry tag sorts last. This is a plain sort on the saved rank — not a score,
which is in Later.

**Search tab** — search and filter every listing in the DB for my selected roles.

**Chat tab** — an LLM with deliberately limited scope: resume feedback, where my
resume falls short, how to learn missing skills. Its only tools are querying the
requirements table, reading my resume versions, and reading my tracker. Nothing
else.

**Profile** — my onboarding answers, editable, plus saved resume versions.

## What happens behind the scenes

The user never sees any of this.

1. Pull listings from the APIs for the roles stored in the DB.
2. Store them in one shared `listings` table. A user's board is a filtered view
   of it by their roles, not a copy.
3. Get the full description per listing. ATS APIs return it directly; for other
   sources, follow a link only when it lands on Greenhouse, Lever, or Ashby.
   Not built now: The Muse already returns full descriptions, so link-following
   is only needed when a source without full text is added.
4. The LLM reads each description and saves requirements: one row per
   requirement with `statement` (the full idea in plain words), `kind`
   (`technology` / `concept` / `experience` / `education` / `other`), and
   `required` or `preferred`.
5. The Chat tab queries that table.

Each listing carries an `industry` tag, taken from the source's own category
where it has one, which is what the preference ranking sorts on. Phase 2 adds
that column.

## Design rules

Full rules in CLAUDE.md. The load-bearing ones:

- Each source is one plain function returning the shared listing dict.
- Only `full_text=True` listings go to requirement extraction.
- Every API call is tracked per source and stops before the provider's limit.
- Prompts live in `prompts/*.txt`. Every LLM call is logged with tokens and cost.
- One real saved response per source in `tests/fixtures/`. Tests never hit a
  live API or an LLM.
- One branch and one PR per phase, CI green before merge.

## Build order

### 1. Onboarding
Four questions as a web form at localhost. Tech majors only; a hardcoded list of
common roles per major is fine to start. Tables: `profile`, `profile_roles`, and
`profile_industries` with a `rank` column, since the order is the signal. The
**Other** button is the one LLM call here, prompt in `prompts/suggest_roles.txt`,
logged like any other. Removes `roles.txt` and with it `roles_file` from
`config.py`, `tests/test_config.py`, and the README.
**done means:** I complete onboarding in the browser and land on a page showing
my saved school, major, roles, and ranked industries, all editable; the real
Dashboard replaces that page in phase 3.

### 2. Fetch and store for my roles
The Muse first, queried per role, as one plain function. Adds the `intern-app
fetch` command and an `industry` column on `listings`, mapped from the Muse
category — via an explicit migration, because `schema.sql` is all
`CREATE TABLE IF NOT EXISTS` and cannot alter a table that already exists on
disk. Saves one real Muse response to `tests/fixtures/`, which is also what
confirms the category field exists. Quota-checked, deduped on url.
**done means:** `intern-app fetch` stores listings for my roles in `listings`
with their industry set, a second run adds no duplicate rows, and an existing
phase-1 database gains the column without losing a row.

### 3. Dashboard and tracker
New jobs for my roles, the status lifecycle with history, the industry filter.
Tables: `tracker` (one row per listing I act on, carrying current status) and
`tracker_history` (one row per status change, which is the history).
**done means:** new listings for my roles show at localhost ordered by my
industry preference, I can move one to `applied` and it survives a restart, and
the industry filter narrows the list.

### 4. Requirements extraction
One row per requirement in a `requirements` table: `listing_id`, `statement`,
`kind`, and `level` as required-or-preferred. Prompt in
`prompts/extract_requirements.txt`.
**done means:** each full-description listing has requirement rows that read as
complete ideas ("experience with Docker", not `docker`), and re-running makes no
second LLM call.

### 5. Search tab
Search and filter all stored listings for my roles.
**done means:** a keyword search at localhost returns matching listings from the
DB, filterable by role and industry.

### 6. Resume versions in Profile
Upload a PDF or paste text; keep every version in a `resumes` table, one row per
version.
**done means:** I upload two resume versions and both are listed newest first,
with the older one still readable.

### 7. Chat tab
Scoped LLM with three tools: requirements table, resume versions, tracker.
**done means:** I ask where my resume falls short for one of my roles and get an
answer citing real requirements from the DB and lines from my resume, and it
declines a question outside its scope.

### 8. Evals
Labeled extraction data, `evals/run.py` prints metrics.
**done means:** `python evals/run.py` prints extraction precision and recall
against the labeled set, with the numbers logged in README.

## Later

Not built now, listed so they are not forgotten: a `concepts` table and concept
merging, requirement depth levels, embedding-based clustering of statements,
non-tech roles, multi-user. Also deferred: Adzuna, USAJobs, ATS board discovery,
Gmail LinkedIn alerts, scoring and ranking, the "save this job" bookmarklet.

The CIP-SOC crosswalk and O*NET title files were verified to exist and parse
(figures in git history on branch `plan-onboarding`); they can seed the
hardcoded role lists, but no code depends on them now.
