"""Reaching a posting's full text through the ATS that publishes an API.

CLAUDE.md allows documented APIs and public board endpoints only. These tests
pin which hosts are in reach and which are deliberately not, so a later change
cannot quietly turn this into a page scraper.
"""

from intern_app.llm import postings
from intern_app.sources import ats_detail


def test_a_greenhouse_link_becomes_its_board_api_call():
    board, url, job_id = ats_detail.api_url(
        "https://boards.greenhouse.io/andurilindustries/jobs/4802146007"
    )

    assert board == "greenhouse"
    assert url == "https://boards-api.greenhouse.io/v1/boards/andurilindustries/jobs/4802146007"
    assert job_id == "4802146007"


def test_a_european_lever_link_uses_the_european_api_host():
    """jobs.eu.lever.co is served by api.eu.lever.co; the US host 404s for it."""
    board, url, _ = ats_detail.api_url(
        "https://jobs.eu.lever.co/cirrus/2926421c-691a-434a-ae59-c828e7fcbf5b"
    )

    assert board == "lever"
    assert url.startswith("https://api.eu.lever.co/v0/postings/cirrus/")


def test_an_ashby_link_points_at_the_whole_board():
    """Ashby has no per-posting endpoint, so the board is fetched once and the
    posting found inside it by id."""
    board, url, job_id = ats_detail.api_url(
        "https://jobs.ashbyhq.com/1x/5b2b4c73-13b5-46ca-8467-8024741a4b57/application"
    )

    assert board == "ashby"
    assert url == "https://api.ashbyhq.com/posting-api/job-board/1x"
    assert job_id == "5b2b4c73-13b5-46ca-8467-8024741a4b57"


def test_a_host_with_no_published_api_is_left_alone():
    """Workday hosts 1,076 of the stored listings and publishes no job API.
    Reading those would mean fetching and parsing the page, which is scraping."""
    for url in (
        "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/x",
        "https://careers-gdms.icims.com/jobs/12345/intern/job",
        "https://www.tesla.com/careers/search/job/1234",
        "https://www.adzuna.com/land/ad/5920433337",
    ):
        assert ats_detail.api_url(url) is None


def test_greenhouse_content_is_unescaped_twice():
    """Greenhouse returns its HTML escaped inside JSON, so one unescape leaves
    the tags as visible text rather than removing them."""
    raw = "&lt;p&gt;We want &lt;b&gt;Python&lt;/b&gt;&amp;nbsp;and SQL.&lt;/p&gt;"

    assert ats_detail.strip_html(raw).replace("\xa0", " ").strip() == "We want Python and SQL."


def test_each_board_is_read_from_its_own_shape():
    assert (
        ats_detail.description_from("greenhouse", {"content": "&lt;p&gt;Hi&lt;/p&gt;"}, "1") == "Hi"
    )
    assert ats_detail.description_from("lever", {"descriptionPlain": "Hi there"}, "1") == "Hi there"
    assert (
        ats_detail.description_from(
            "ashby",
            {"jobs": [{"id": "abc", "descriptionPlain": "Mine"}, {"id": "xyz"}]},
            "abc",
        )
        == "Mine"
    )


def test_a_posting_missing_from_its_board_reads_as_empty(conn):
    assert ats_detail.description_from("ashby", {"jobs": [{"id": "other"}]}, "mine") == ""


def test_only_listings_without_full_text_are_fetched(conn, listing):
    from intern_app import db

    db.upsert_listings(
        conn,
        [
            listing("https://boards.greenhouse.io/acme/jobs/1", full_text=False),
            listing("https://boards.greenhouse.io/acme/jobs/2", full_text=True),
            listing("https://nvidia.wd5.myworkdayjobs.com/x/job/3", full_text=False),
        ],
    )

    pending = [row["url"] for row in ats_detail.listings_needing_description(conn)]

    assert pending == ["https://boards.greenhouse.io/acme/jobs/1"]


def test_storing_a_description_opens_the_full_text_gate(conn, listing):
    from intern_app import db

    db.upsert_listings(conn, [listing("https://x.com/a", full_text=False)])
    row_id = conn.execute("SELECT id FROM listings").fetchone()["id"]

    ats_detail.store_description(conn, row_id, "The whole posting.")

    stored = conn.execute("SELECT description, full_text FROM listings").fetchone()
    assert stored["description"] == "The whole posting."
    assert stored["full_text"] == 1


def test_a_reading_outside_the_known_set_is_corrected_not_stored():
    """The board filters on these, so an unknown value would hide a listing."""
    assert postings.one_of("PhD", postings.EDUCATION, "any") == "phd"
    assert postings.one_of("bachelors", postings.EDUCATION, "any") == "any"
    assert postings.one_of("", postings.LEVELS, "other") == "other"


def test_a_posting_already_read_is_not_read_again(conn, listing):
    """Rereading 851 postings because the pass was run twice is a real cost."""
    from intern_app import db

    db.upsert_listings(conn, [listing("https://x.com/a", description="x" * 300, full_text=True)])
    row_id = conn.execute("SELECT id FROM listings").fetchone()["id"]

    assert len(postings.listings_with_unread_descriptions(conn)) == 1

    db.record_llm_call(
        conn,
        prompt_name="read_posting",
        model="claude-haiku-5-5",
        listing_id=row_id,
        ok=True,
    )

    assert postings.listings_with_unread_descriptions(conn) == []
