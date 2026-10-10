from datetime import UTC, datetime, timedelta

import pytest

from intern_app import db
from intern_app.llm import pricing

MODEL = "claude-opus-5-5"


def test_insert_then_resight_does_not_duplicate(conn, listing):
    assert db.upsert_listings(conn, [listing()]) == (1, 0)
    assert db.upsert_listings(conn, [listing()]) == (0, 1)
    assert conn.execute("SELECT COUNT(*) FROM listings").fetchone()[0] == 1


def test_resight_keeps_first_seen_and_moves_last_seen(conn, listing):
    db.upsert_listings(conn, [listing()])
    conn.execute("UPDATE listings SET first_seen = '2026-01-01T00:00:00+00:00'")
    db.upsert_listings(conn, [listing(title="Senior Intern")])
    row = conn.execute("SELECT * FROM listings").fetchone()
    assert row["first_seen"] == "2026-01-01T00:00:00+00:00"
    assert row["last_seen"] > row["first_seen"]
    assert row["title"] == "Senior Intern"


def test_a_discovery_only_resight_cannot_erase_a_full_description(conn, listing):
    """Adzuna seeing a job we already have the full text of must not blank it."""
    db.upsert_listings(conn, [listing()])
    db.upsert_listings(conn, [listing(full_text=False, source="adzuna")])
    row = conn.execute("SELECT * FROM listings").fetchone()
    assert row["description"] == "We want Python and SQL."
    assert row["full_text"] == 1


def test_a_full_text_sighting_upgrades_a_discovery_only_row(conn, listing):
    db.upsert_listings(conn, [listing(full_text=False, source="adzuna")])
    db.upsert_listings(conn, [listing()])
    row = conn.execute("SELECT * FROM listings").fetchone()
    assert row["full_text"] == 1
    assert row["description"] == "We want Python and SQL."


def test_extraction_queue_excludes_truncated_listings(conn, listing):
    db.upsert_listings(conn, [listing("https://example.com/a")])
    db.upsert_listings(conn, [listing("https://example.com/b", full_text=False, source="adzuna")])
    urls = [row["url"] for row in db.listings_needing_extraction(conn)]
    assert urls == ["https://example.com/a"]


def test_extraction_queue_excludes_already_extracted(conn, listing):
    db.upsert_listings(conn, [listing()])
    listing_id = conn.execute("SELECT id FROM listings").fetchone()["id"]
    db.record_llm_call(conn, prompt_name="extract_skills", model=MODEL, listing_id=listing_id)
    assert db.listings_needing_extraction(conn) == []


def test_a_failed_extraction_leaves_the_listing_in_the_queue(conn, listing):
    db.upsert_listings(conn, [listing()])
    listing_id = conn.execute("SELECT id FROM listings").fetchone()["id"]
    db.record_llm_call(
        conn, prompt_name="extract_skills", model=MODEL, listing_id=listing_id, ok=False
    )
    assert len(db.listings_needing_extraction(conn)) == 1


def test_api_calls_count_within_a_window(conn):
    db.record_api_call(conn, source="adzuna")
    db.record_api_call(conn, source="adzuna", ok=False, status_code=500)
    db.record_api_call(conn, source="muse")
    assert db.calls_in_last(conn, "adzuna", days=1) == 2
    assert db.calls_in_last(conn, "muse", days=1) == 1


def test_calls_outside_the_window_are_not_counted(conn):
    old = (datetime.now(UTC) - timedelta(days=40)).isoformat(timespec="seconds")
    conn.execute(
        "INSERT INTO api_calls (source, called_at, ok) VALUES ('adzuna', ?, 1)",
        (old,),
    )
    assert db.calls_in_last(conn, "adzuna", days=30) == 0


def test_last_call_at_is_empty_for_an_unused_source(conn):
    assert db.last_call_at(conn, "lever") == ""


def test_llm_spend_sums_cost_and_tokens(conn):
    db.record_llm_call(conn, prompt_name="p", model=MODEL, input_tokens=1000, output_tokens=200)
    db.record_llm_call(conn, prompt_name="p", model=MODEL, input_tokens=500, output_tokens=100)
    spend = db.llm_spend(conn)
    assert spend["calls"] == 2
    assert spend["input_tokens"] == 1500
    # Cost is computed at write time from the model, not supplied by the caller.
    assert spend["cost_usd"] > 0


def test_llm_spend_on_an_empty_log_is_zero_not_null(conn):
    assert db.llm_spend(conn, days=30) == {
        "calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": 0.0,
    }


def test_source_counts(conn, listing):
    db.upsert_listings(conn, [listing("https://example.com/a")])
    db.upsert_listings(conn, [listing("https://example.com/b", full_text=False, source="adzuna")])
    rows = {r["source"]: r for r in db.source_counts(conn)}
    assert rows["muse"]["with_full_text"] == 1
    assert rows["adzuna"]["with_full_text"] == 0


def test_an_endpoint_query_string_is_never_stored(conn):
    """Adzuna, Muse, and USAJobs put credentials in the query string."""
    db.record_api_call(
        conn,
        source="adzuna",
        endpoint="https://api.adzuna.com/v1/api/jobs/us/search/1?app_key=super-secret&what=intern",
    )
    stored = conn.execute("SELECT endpoint FROM api_calls").fetchone()["endpoint"]
    assert stored == "https://api.adzuna.com/v1/api/jobs/us/search/1"
    assert "super-secret" not in stored


def test_cost_is_computed_at_write_time_not_supplied(conn):
    db.record_llm_call(conn, prompt_name="p", model=MODEL, input_tokens=8000, output_tokens=500)
    row = conn.execute("SELECT cost_usd FROM llm_calls").fetchone()
    assert row["cost_usd"] == pytest.approx(0.042)


def test_logging_a_call_on_an_unpriced_model_fails_loudly(conn):
    with pytest.raises(pricing.UnknownModel):
        db.record_llm_call(conn, prompt_name="p", model="mystery-model", input_tokens=10)


def test_a_non_extraction_call_does_not_mark_a_listing_extracted(conn, listing):
    """A later ranking call on the same listing must not hide it from extraction."""
    db.upsert_listings(conn, [listing()])
    listing_id = conn.execute("SELECT id FROM listings").fetchone()["id"]
    db.record_llm_call(conn, prompt_name="rank_listing", model=MODEL, listing_id=listing_id)
    assert len(db.listings_needing_extraction(conn)) == 1
