# intern-app

Aggregates internship and entry-level listings from job APIs, extracts the skills
each posting actually requires using Claude, ranks them against my profile, and
serves the result on a local dashboard.

Role-first: I manage a list of role title variants in `roles.txt` and nothing
else. Company job boards are discovered automatically and never user-managed.

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
| The Muse | free | yes | queried per role variant, Internship / Entry Level |
| Greenhouse / Lever / Ashby | none | yes | internal: slugs auto-discovered into `ats_boards` |
| Adzuna | free, ~1k calls/month | no | queried per role variant, discovery only |
| USAJobs | free | yes | queried per role variant, federal only |
| Gmail job alerts | OAuth, read-only | no | LinkedIn alert emails; title/company/location/url only |

Only listings with `full_text=True` are sent to skill extraction. Adzuna results
carry the required "Jobs by Adzuna" attribution wherever they are displayed.

## Layout

```
roles.txt          role title variants — the only targeting setting
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
- [x] Phase 1 — SQLite storage, quota tracking, LLM call log
- [ ] Phase 2 — role variants and The Muse
- [ ] Phase 3 — Adzuna
- [ ] Phase 4 — USAJobs
- [ ] Phase 5 — ATS board discovery and pulling
- [ ] Phase 6 — Gmail LinkedIn alerts
- [ ] Phase 7 — skill extraction and evals
- [ ] Phase 8 — profile and ranking
- [ ] Phase 9 — dashboard
