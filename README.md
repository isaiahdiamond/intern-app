# intern-app

Aggregates internship and entry-level listings from job APIs, extracts the skills
each posting actually requires using Claude, ranks them against my profile, and
serves the result on a local dashboard.

Role-first: onboarding asks for my school, major, target roles and preferred
industries, and that profile drives everything. Company job boards are
discovered automatically and never user-managed.

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
| GitHub internship repos | none | no | 10 repos, US + remote, role-filtered, twice daily |
| Greenhouse / Lever / Ashby | none | yes | slugs auto-discovered from apply links |
| Adzuna | free, ~1k calls/month | no | queried per role variant, discovery only |
| USAJobs | free | yes | whole student/grad pool in one call, federal only |
| LinkedIn alerts | Yahoo app password | no | read-only IMAP, job-alert sender only |

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
intern-app serve      # onboarding + dashboard at http://127.0.0.1:8000
intern-app fetch      # pull from The Muse and the GitHub repos
intern-app classify   # give each company an industry
```

### Daily use

```bash
intern-app fetch && intern-app classify && intern-app serve
```

CI runs both on every push and pull request. Tests and evals read fixtures and
never touch a live API or make an LLM call.

## Eval results

Logged here as each eval lands.

| Date | Eval | Metric | Result |
|---|---|---|---|
| — | — | — | not yet run |

## Build status

Phases follow PLAN.md.

- [x] Repo, tooling, CI, source contract
- [x] SQLite storage, quota tracking, LLM call log
- [x] Phase 1 — onboarding and the profile
- [x] Phase 2 — fetch and store for my roles (The Muse)
- [x] Phase 3 — dashboard and tracker
- [ ] Phase 4 — requirements extraction
- [ ] Phase 5 — search tab
- [ ] Phase 6 — resume versions in profile
- [ ] Phase 7 — chat tab
- [ ] Phase 8 — evals
