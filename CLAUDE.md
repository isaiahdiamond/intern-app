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

## Workflow

- One branch per phase, one PR per branch, CI green before merge.
- `ruff check` and `ruff format` clean; `pytest` green.
- Run the `reviewer` subagent before every commit.
