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


def test_a_fresh_source_may_call(conn):
    quota.check(conn, "adzuna")


def test_remaining_subtracts_the_reserve(conn):
    # adzuna: 50/day, reserve 25 -> 25 spendable before any calls.
    assert quota.remaining(conn, "adzuna") == 25


def test_remaining_is_none_when_a_source_has_no_ceiling(conn):
    assert quota.remaining(conn, "greenhouse") is None


def test_the_reserve_blocks_before_the_real_limit(conn):
    backdate_calls(conn, "adzuna", 25, hours_ago=1)
    assert quota.remaining(conn, "adzuna") == 0
    with pytest.raises(quota.QuotaExceeded, match="calls left in budget"):
        quota.check(conn, "adzuna")


def test_the_monthly_ceiling_binds_even_when_today_is_quiet(conn):
    backdate_calls(conn, "adzuna", 980, days_ago=10)
    assert quota.remaining(conn, "adzuna") == 0
    with pytest.raises(quota.QuotaExceeded):
        quota.check(conn, "adzuna")


def test_needed_is_respected(conn):
    backdate_calls(conn, "adzuna", 20, hours_ago=1)
    assert quota.remaining(conn, "adzuna") == 5
    quota.check(conn, "adzuna", needed=5)
    with pytest.raises(quota.QuotaExceeded, match="6 needed"):
        quota.check(conn, "adzuna", needed=6)


def test_polling_a_board_too_soon_is_refused(conn):
    db.record_api_call(conn, source="greenhouse")
    with pytest.raises(quota.QuotaExceeded, match=r"floor is 3\.0h"):
        quota.check(conn, "greenhouse")


def test_polling_a_board_after_the_floor_is_allowed(conn):
    backdate_calls(conn, "greenhouse", 1, hours_ago=4)
    quota.check(conn, "greenhouse")


def test_may_call_is_the_non_raising_form(conn):
    db.record_api_call(conn, source="greenhouse")
    assert quota.may_call(conn, "greenhouse") is False
    assert quota.may_call(conn, "lever") is True


def test_an_unknown_source_gets_the_conservative_default(conn):
    assert quota.limit_for("brand-new-board").min_interval_hours == 1.0
    db.record_api_call(conn, source="brand-new-board")
    assert quota.may_call(conn, "brand-new-board") is False


def test_failed_calls_still_spend_quota(conn):
    """A 500 consumed a request as far as the provider is concerned."""
    for _ in range(25):
        db.record_api_call(conn, source="adzuna", ok=False, status_code=500)
    assert quota.remaining(conn, "adzuna") == 0


def test_a_paginating_run_can_skip_the_interval_floor(conn):
    """Page one must not make page two look like a too-recent poll."""
    quota.check(conn, "greenhouse")
    db.record_api_call(conn, source="greenhouse")
    with pytest.raises(quota.QuotaExceeded):
        quota.check(conn, "greenhouse")
    quota.check(conn, "greenhouse", check_interval=False)


def test_skipping_the_interval_still_enforces_the_budget(conn):
    backdate_calls(conn, "adzuna", 25, hours_ago=1)
    with pytest.raises(quota.QuotaExceeded, match="calls left in budget"):
        quota.check(conn, "adzuna", check_interval=False)
