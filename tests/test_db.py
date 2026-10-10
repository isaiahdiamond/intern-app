import pytest

from intern_app import db
from intern_app.llm import pricing

MODEL = "claude-opus-5-5"


def test_resighting_a_listing_updates_it_instead_of_duplicating(conn, listing):
    assert db.upsert_listings(conn, [listing()]) == (1, 0)
    conn.execute("UPDATE listings SET first_seen = '2026-01-01T00:00:00+00:00'")

    assert db.upsert_listings(conn, [listing(title="Senior Intern")]) == (0, 1)

    row = conn.execute("SELECT * FROM listings").fetchone()
    assert row["first_seen"] == "2026-01-01T00:00:00+00:00"
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


def test_extraction_queue_only_holds_unextracted_full_text_listings(conn, listing):
    db.upsert_listings(conn, [listing("https://example.com/full")])
    db.upsert_listings(conn, [listing("https://example.com/thin", full_text=False)])

    assert [row["url"] for row in db.listings_needing_extraction(conn)] == [
        "https://example.com/full"
    ]

    listing_id = conn.execute(
        "SELECT id FROM listings WHERE url = 'https://example.com/full'"
    ).fetchone()["id"]
    db.record_llm_call(conn, prompt_name="extract_skills", model=MODEL, listing_id=listing_id)
    assert db.listings_needing_extraction(conn) == []


def test_a_failed_or_unrelated_call_leaves_the_listing_in_the_queue(conn, listing):
    db.upsert_listings(conn, [listing()])
    listing_id = conn.execute("SELECT id FROM listings").fetchone()["id"]

    db.record_llm_call(
        conn, prompt_name="extract_skills", model=MODEL, listing_id=listing_id, ok=False
    )
    db.record_llm_call(conn, prompt_name="rank_listing", model=MODEL, listing_id=listing_id)

    assert len(db.listings_needing_extraction(conn)) == 1


def test_an_endpoint_query_string_is_never_stored(conn):
    """Adzuna, Muse, and USAJobs all put credentials in the query string."""
    db.record_api_call(
        conn,
        source="adzuna",
        endpoint="https://api.adzuna.com/v1/api/jobs/us/search/1?app_key=super-secret&what=intern",
    )

    stored = conn.execute("SELECT endpoint FROM api_calls").fetchone()["endpoint"]
    assert stored == "https://api.adzuna.com/v1/api/jobs/us/search/1"


def test_cost_is_computed_at_write_time_not_supplied(conn):
    db.record_llm_call(conn, prompt_name="p", model=MODEL, input_tokens=8000, output_tokens=500)

    row = conn.execute("SELECT cost_usd FROM llm_calls").fetchone()
    assert row["cost_usd"] == pytest.approx(0.042)


def test_logging_a_call_on_an_unpriced_model_fails_loudly(conn):
    with pytest.raises(pricing.UnknownModelError):
        db.record_llm_call(conn, prompt_name="p", model="mystery-model", input_tokens=10)


def test_spend_sums_calls_tokens_and_cost(conn):
    """The status report reads these sums, so the SUM/COUNT logic is load-bearing."""
    db.record_llm_call(conn, prompt_name="p", model=MODEL, input_tokens=1000, output_tokens=200)
    db.record_llm_call(conn, prompt_name="p", model=MODEL, input_tokens=500, output_tokens=100)

    spend = db.llm_spend(conn, days=30)
    assert spend["calls"] == 2
    assert spend["input_tokens"] == 1500
    assert spend["cost_usd"] > 0


def test_spend_on_an_empty_log_is_zero_not_null(conn):
    assert db.llm_spend(conn, days=30) == {
        "calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": 0.0,
    }
