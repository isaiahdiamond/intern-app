from datetime import UTC, datetime, timedelta

import pytest

from intern_app import db
from intern_app.sources import quota


def backdate_calls(conn, source, count, *, days_ago=0, hours_ago=0):
    when = (datetime.now(UTC) - timedelta(days=days_ago, hours=hours_ago)).isoformat(
        timespec="seconds"
    )
    conn.executemany(
        "INSERT INTO api_calls (source, called_at, ok) VALUES (?, ?, 1)",
        [(source, when)] * count,
    )


def test_a_fresh_source_may_call_and_sees_its_budget(conn):
    quota.check(conn, "adzuna")
    # adzuna is 50/day with 25 held in reserve.
    assert quota.remaining(conn, "adzuna") == 25
    assert quota.remaining(conn, "greenhouse") is None


def test_the_reserve_blocks_before_the_real_limit(conn):
    # Backdated past adzuna's 6-hour floor, so this tests the budget alone.
    backdate_calls(conn, "adzuna", 25, hours_ago=7)

    assert quota.remaining(conn, "adzuna") == 0
    with pytest.raises(quota.QuotaExceededError, match="calls left in budget"):
        quota.check(conn, "adzuna")


def test_the_monthly_ceiling_binds_even_when_today_is_quiet(conn):
    backdate_calls(conn, "adzuna", 980, days_ago=10)

    with pytest.raises(quota.QuotaExceededError):
        quota.check(conn, "adzuna")


def test_needed_is_respected(conn):
    backdate_calls(conn, "adzuna", 20, hours_ago=7)

    quota.check(conn, "adzuna", needed=5)
    with pytest.raises(quota.QuotaExceededError, match="6 needed"):
        quota.check(conn, "adzuna", needed=6)


def test_polling_a_board_too_soon_is_refused(conn):
    db.record_api_call(conn, source="greenhouse")

    with pytest.raises(quota.QuotaExceededError, match=r"floor is 3\.0h"):
        quota.check(conn, "greenhouse")

    backdate_calls(conn, "lever", 1, hours_ago=4)
    quota.check(conn, "lever")


def test_a_paginating_run_skips_the_clock_but_never_the_budget(conn):
    """Page one must not make page two look like a too-recent poll.

    The flag waives the polling floor only. A run that has spent its budget is
    still refused, or a paginating source could blow past a provider's ceiling.
    """
    db.record_api_call(conn, source="greenhouse")
    quota.check(conn, "greenhouse", check_interval=False)
    assert quota.may_call(conn, "greenhouse") is False

    backdate_calls(conn, "adzuna", 25, hours_ago=7)
    with pytest.raises(quota.QuotaExceededError, match="calls left in budget"):
        quota.check(conn, "adzuna", check_interval=False)


def test_an_old_call_stops_counting_against_the_budget(conn):
    """If the window filter broke, a source would count all-time calls and
    lock itself out permanently."""
    backdate_calls(conn, "adzuna", 40, days_ago=40)

    assert db.calls_in_last(conn, "adzuna", days=30) == 0
    assert quota.remaining(conn, "adzuna") == 25


def test_a_repeated_run_is_refused_by_the_poll_floor(conn):
    """One run costs a call per role, so two runs in an hour nearly drained
    adzuna's spendable daily budget before the floor was added."""
    db.record_api_call(conn, source="adzuna")

    with pytest.raises(quota.QuotaExceededError, match=r"floor is 6\.0h"):
        quota.check(conn, "adzuna")


def test_failed_calls_still_spend_quota(conn):
    """A 500 consumed a request as far as the provider is concerned."""
    for _ in range(25):
        db.record_api_call(conn, source="adzuna", ok=False, status_code=500)

    assert quota.remaining(conn, "adzuna") == 0


def test_an_unknown_source_gets_the_conservative_default(conn):
    assert quota.limit_for("brand-new-board").min_interval_hours == 1.0

    db.record_api_call(conn, source="brand-new-board")
    assert quota.may_call(conn, "brand-new-board") is False
