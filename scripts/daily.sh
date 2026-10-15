#!/bin/bash
# The daily pull. Runs under launchd twice a day; see scripts/README.md.
#
# Every step is skipped rather than failed when its quota or budget is gone,
# because a half-finished run that leaves the board more current than it was
# is worth more than an aborted one. The steps are ordered so the cheap ones
# happen first: if the LLM budget is exhausted the listings are still there,
# just not yet cleaned.

set -u
cd "$(dirname "$0")/.." || exit 1

PYTHON=".venv/bin/python"
LOG="data/daily.log"
MAX_CLEAN=400   # titles per run; a backlog is cleaned over several days

exec >>"$LOG" 2>&1
echo "=== $(date '+%Y-%m-%d %H:%M:%S %Z') ==="

if [ ! -x "$PYTHON" ]; then
    echo "no virtualenv at $PYTHON — did the project move?"
    exit 1
fi

run() {
    echo "--- $1"
    shift
    "$PYTHON" -m intern_app.cli "$@" || echo "    step failed, carrying on"
}

# New listings. Sources that are out of quota report it and are skipped.
run "fetch" fetch

# Industry for any company we have not seen before. Cheap, and the board
# sorts on it.
run "classify" classify --yes

# Titles. Capped per run so one big fetch cannot spend the month's budget in
# a morning; whatever is left is picked up by the next run.
run "clean" clean --limit "$MAX_CLEAN" --yes

# Favicons. No LLM call for a company whose domain is already known.
run "icons" icons --yes

# Full descriptions from documented ATS APIs. No LLM call, so no budget
# prompt and no --yes.
run "describe" describe
run "read" read --limit "$MAX_CLEAN" --yes

echo "--- done $(date '+%H:%M:%S')"
"$PYTHON" -m intern_app.cli status | tail -3
echo
