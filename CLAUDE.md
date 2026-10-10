# CLAUDE.md

Internship aggregator. Pulls listings from job APIs, extracts required skills with
Claude, ranks them against my profile, and serves a local dashboard.

Python 3.12. Package lives in `src/intern_app/`.

## Hard rules

1. **No scraping.** Only documented APIs and public board endpoints. No LinkedIn
   scraping ever — LinkedIn data arrives only via job-alert emails from my Gmail.
2. **No secrets in the repo.** Keys come from `.env` (gitignored) through
   `config.py`. Never hardcode a key, never commit `.env`, never print a key or a
   token in a log line, error message, or test fixture. `.env.example` holds names
   with empty values only.
3. **Respect rate limits.** Every outbound API call is recorded in `api_calls`. A
   source must check its remaining quota before calling and stop short of the
   limit. Poll board endpoints at most every few hours.
4. **Fixtures, not live APIs, in tests.** Tests and evals read
   `tests/fixtures/`. No test makes a network call or an LLM call.
5. **Every LLM call is logged** to `llm_calls` with prompt name, model, input and
   output tokens, and computed cost. No un-logged call path.

## Source contract

Each source is one plain function in `src/intern_app/sources/<name>.py`. It returns
a list of dicts, every dict exactly this shape:

```python
{
    "title": str,
    "company": str,
    "location": str,
    "url": str,  # canonical, deduped on
    "description": str,  # "" when full_text is False
    "posted_at": str,  # ISO 8601 date or datetime, "" if unknown
    "source": str,  # the source's name
    "full_text": bool,  # True only if description is the complete posting
}
```

Only listings with `full_text=True` go to skill extraction. A source that returns
truncated or absent descriptions sets `full_text=False` and is for discovery only.

Normalize through `sources.base`, don't hand-roll per source.

## Prompts

Prompt text lives in `prompts/*.txt`, one file per prompt, loaded by name. No
prompt strings inline in Python. Changing a prompt is a reviewable diff.

## Attribution

Adzuna results must be shown with "Jobs by Adzuna" wherever they surface.
USAJobs requires my registered email as the `User-Agent`.

## Code style

Written to be read by someone new to the codebase. Clear beats clever, and clear
beats short.

- **PEP 8, enforced by ruff.** `snake_case` for variables and functions,
  `UPPER_CASE` for module constants, `CapWords` for the few classes.
- **Functions are named for what they do** — `load_roles`, `fetch_muse`,
  `match_title`. A function whose name is a noun is usually a value in disguise.
- **Names are whole words, no padding.** `role`, not `r`, and not
  `role_title_variant_string`. One or two words is the target.
- **No code golf.** A triple-nested comprehension, a walrus that saves one line,
  or a clever one-liner that needs a comment to decode: write the plain loop
  instead. Shortest is not the goal.
- **Comments say why, not what.** If a line needs a comment explaining what it
  does, rename something instead.
- **Each source is one plain function** — see the source contract above.
- **No new dependency without asking first.**
- **Tests earn their place.** One test per distinct failure that could really
  happen. No test that restates another one with different data.

## Design

DESIGN.md is the source of truth for all UI. Read it before creating or changing
any frontend file. Use its tokens and components exactly; don't invent new
colors, sizes or styles. If something isn't covered, ask me.

`designer.md` holds the staged prompts for building the MVP UI, in order.

## Frontend code style

Write code for a human beginner to read. Simple, flat, procedural. Function
components only, no classes, no custom hooks or abstraction layers unless I ask.
Short names. No comments that explain what code does. No try/catch except around
network and file I/O. Use built-ins over custom helpers. No placeholder tests or
boilerplate.

## Workflow

- One branch per phase, one PR per branch, CI green before merge.
- `ruff check` and `ruff format` clean; `pytest` green.
- Before every commit, run the reviewer agent on the diff, then the verifier
  agent on the current task. Fix all FAIL items before committing.
