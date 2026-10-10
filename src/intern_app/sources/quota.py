"""Per-source rate limits, enforced against the `api_calls` table.

A source calls `check` before every outbound request and `db.record_api_call`
after. The limits below are the free-tier ceilings; `reserve` keeps a margin so a
run never lands exactly on the limit.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from intern_app import db


class QuotaExceededError(RuntimeError):
    """A source has no remaining budget, or was polled too recently."""


@dataclass(frozen=True)
class Limit:
    """A source's call budget.

    `per_month` / `per_day` are hard ceilings from the provider's free tier.
    `min_interval_hours` keeps polite spacing on endpoints that have no published
    limit — the public board endpoints, which we poll every few hours at most.
    `reserve` is how many calls we refuse to spend, so a surprise retry or a
    paginated response cannot push us over.
    """

    per_month: int | None = None
    per_day: int | None = None
    min_interval_hours: float = 0.0
    reserve: int = 0


# Adzuna's free tier is ~1,000 calls/month and it is discovery-only, so it gets
# the tightest accounting. The board endpoints publish no limit; we self-impose
# a 3-hour floor. The Muse and USAJobs are generous but not unlimited.
LIMITS: dict[str, Limit] = {
    "adzuna": Limit(per_month=1000, per_day=50, reserve=25),
    "muse": Limit(per_day=500, min_interval_hours=1.0, reserve=10),
    "usajobs": Limit(per_day=500, min_interval_hours=1.0, reserve=10),
    "greenhouse": Limit(min_interval_hours=3.0),
    "lever": Limit(min_interval_hours=3.0),
    "ashby": Limit(min_interval_hours=3.0),
    "gmail": Limit(per_day=200, min_interval_hours=1.0, reserve=10),
    "jsearch": Limit(per_month=200, reserve=10),
}

DEFAULT_LIMIT = Limit(min_interval_hours=1.0)


def limit_for(source: str) -> Limit:
    return LIMITS.get(source, DEFAULT_LIMIT)


def remaining(conn: sqlite3.Connection, source: str) -> int | None:
    """Calls left before the tightest ceiling, or None when there is no ceiling.

    The reserve is already subtracted, so this is the number actually spendable.
    """
    limit = limit_for(source)
    budgets = []
    if limit.per_month is not None:
        budgets.append(limit.per_month - limit.reserve - db.calls_in_last(conn, source, days=30))
    if limit.per_day is not None:
        budgets.append(limit.per_day - limit.reserve - db.calls_in_last(conn, source, days=1))
    if not budgets:
        return None
    return max(0, min(budgets))


def check(
    conn: sqlite3.Connection,
    source: str,
    *,
    needed: int = 1,
    check_interval: bool = True,
) -> None:
    """Raise `QuotaExceededError` unless `source` may make `needed` more calls now.

    The minimum-interval floor gates a *run*, not each request: call this once
    before a source starts, with `needed` set to the number of calls the run
    expects. A paginating loop that re-checks its remaining budget part-way
    through passes `check_interval=False`, otherwise its own first page would
    look like a too-recent poll and block page two.
    """
    limit = limit_for(source)

    if check_interval and limit.min_interval_hours:
        last = db.last_call_at(conn, source)
        if last:
            elapsed = datetime.now(UTC) - datetime.fromisoformat(last)
            wait = timedelta(hours=limit.min_interval_hours) - elapsed
            if wait > timedelta(0):
                minutes = int(wait.total_seconds() // 60) + 1
                raise QuotaExceededError(
                    f"{source} was polled {int(elapsed.total_seconds() // 60)} min ago; "
                    f"its floor is {limit.min_interval_hours}h — wait {minutes} min."
                )

    left = remaining(conn, source)
    if left is not None and left < needed:
        raise QuotaExceededError(
            f"{source} has {left} calls left in budget (reserve {limit.reserve} held back); "
            f"{needed} needed. Skipping."
        )


def may_call(
    conn: sqlite3.Connection,
    source: str,
    *,
    needed: int = 1,
    check_interval: bool = True,
) -> bool:
    """Non-raising form, for a collector that skips a source and keeps going."""
    try:
        check(conn, source, needed=needed, check_interval=check_interval)
    except QuotaExceededError:
        return False
    return True
