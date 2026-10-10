# intern-app

Aggregates internship and entry-level listings from job APIs, extracts the skills
each posting actually requires using Claude, ranks them against my profile, and
serves the result on a local dashboard.

No scraping. Every listing comes from a documented API, a public job-board
endpoint, or a job-alert email in my own inbox.

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
cp .env.example .env     # then fill in the keys you have
intern-app config        # shows which credentials are set
```

`.env` is gitignored. No key is ever committed, logged, or printed.

## Sources

| Source | Key | Full text | Notes |
|---|---|---|---|
| The Muse | free | yes | filtered to Internship / Entry Level, multi-industry |
| Greenhouse / Lever / Ashby | none | yes | public board endpoints, slugs in `companies.txt` |
| Adzuna | free, ~1k calls/month | no | discovery only — descriptions are truncated |
| USAJobs | free | yes | federal only |
| Gmail job alerts | OAuth, read-only | no | LinkedIn alert emails; title/company/location/url only |

Only listings with `full_text=True` are sent to skill extraction. Adzuna results
carry the required "Jobs by Adzuna" attribution wherever they are displayed.

## Layout

```
src/intern_app/
  config.py        environment and settings
  sources/         one module per source, shared contract in base.py
  llm/             Claude client, prompt loading, cost logging
  server/          FastAPI dashboard
prompts/           prompt text, one .txt per prompt
evals/             labeled data and run.py
tests/fixtures/    one real saved response per source
```

## Development

```bash
ruff check . && ruff format --check .
pytest
```

CI runs both on every push and pull request. Tests and evals read fixtures and
never touch a live API or make an LLM call.

## Eval results

Logged here as each eval lands.

| Date | Eval | Metric | Result |
|---|---|---|---|
| — | — | — | not yet run |

## Build status

- [x] Phase 0 — repo, tooling, CI, source contract
- [ ] Phase 1 — SQLite storage, quota tracking, LLM call log
- [ ] Phase 2 — sources
- [ ] Phase 3 — skill extraction and evals
- [ ] Phase 4 — profile and ranking
- [ ] Phase 5 — dashboard
