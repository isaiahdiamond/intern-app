"""USAJobs, driven from the saved real response.

Two rules of theirs are load-bearing and tested here: the User-Agent must be my
registered email, and the API key must never be logged.
"""

import json
from pathlib import Path

import pytest

from intern_app import config, db
from intern_app.sources import usajobs

FIXTURE = Path(__file__).parent / "fixtures" / "usajobs_search.json"


@pytest.fixture(scope="module")
def postings():
    payload = json.loads(FIXTURE.read_text())
    return [
        item["MatchedObjectDescriptor"] for item in payload["SearchResult"]["SearchResultItems"]
    ]


def by_title(postings, prefix):
    for descriptor in postings:
        if descriptor["PositionTitle"].lower().startswith(prefix.lower()):
            return descriptor
    raise AssertionError(f"no posting starting with {prefix!r} in the fixture")


def test_the_user_agent_is_my_registered_email(monkeypatch):
    """USAJobs rejects a request whose User-Agent is not the address on file."""
    monkeypatch.setenv("USAJOBS_EMAIL", "me@example.com")
    monkeypatch.setenv("USAJOBS_API_KEY", "not-a-real-key")
    config.settings.cache_clear()

    headers = usajobs.request_headers()

    assert headers["User-Agent"] == "me@example.com"
    assert headers["Host"] == "data.usajobs.gov"
    assert headers["Authorization-Key"] == "not-a-real-key"


def test_a_missing_email_fails_loudly_rather_than_being_rejected_upstream(monkeypatch):
    monkeypatch.setenv("USAJOBS_API_KEY", "not-a-real-key")
    monkeypatch.setenv("USAJOBS_EMAIL", "")
    config.settings.cache_clear()

    with pytest.raises(config.MissingConfigError, match="USAJOBS_EMAIL"):
        usajobs.request_headers()


def test_the_api_key_is_never_written_to_the_call_log(conn):
    """The endpoint is recorded without a query string, and the key rides in a
    header, so nothing should be able to carry it into the database."""
    db.record_api_call(conn, source=usajobs.SOURCE, endpoint=usajobs.ENDPOINT, ok=True)

    stored = conn.execute("SELECT endpoint, error FROM api_calls").fetchone()
    assert "?" not in stored["endpoint"]
    assert stored["error"] == ""


def test_a_real_posting_normalizes_to_the_contract(postings):
    listing = usajobs.to_listing(by_title(postings, "Mathematician"))

    assert listing["title"] == "Mathematician"
    assert listing["source"] == "usajobs"
    assert listing["full_text"] is True
    assert listing["url"].startswith("https://www.usajobs.gov")
    assert listing["location"]
    assert len(listing["posted_at"]) == 10


def test_the_description_is_assembled_from_the_fields_it_is_split_across(postings):
    """JobSummary and MajorDuties live under UserArea.Details, and
    QualificationSummary is top level. MajorDuties arrives as a list."""
    descriptor = by_title(postings, "Computer Scientist")

    text = usajobs.description_of(descriptor)

    assert len(text) > 1000
    details = descriptor["UserArea"]["Details"]
    assert isinstance(details["MajorDuties"], list)
    assert "<" not in usajobs.to_listing(descriptor)["description"][:200]


def test_a_list_field_flattens_and_a_missing_one_is_empty():
    assert usajobs.as_text(["one", "two"]) == "one two"
    assert usajobs.as_text("plain") == "plain"
    assert usajobs.as_text(None) == ""


@pytest.mark.parametrize(
    ("prefix", "role"),
    [
        ("Mathematician", "Mathematician Intern"),
        ("Computer Scientist", "Computer Scientist Intern"),
        ("Mechanical Engineer", "Mechanical Engineer Intern"),
        ("Operations Research Analyst", "Operations Research Intern"),
        ("COMPUTER SCIENCE INTERN", "Computer Scientist Intern"),
        ("Survey Statistician", "Statistician Intern"),
    ],
)
def test_federal_titles_match_the_role_chips_that_exist(prefix, role, postings):
    """These are the real titles the live pool returns. If the matcher stops
    recognising them, the federal source silently returns nothing."""
    from intern_app.sources.role_match import title_matches_role

    assert title_matches_role(by_title(postings, prefix)["PositionTitle"], role) is True


def test_unrelated_federal_postings_do_not_match_my_roles(postings):
    from intern_app.sources.role_match import title_matches_role

    roles = ["Software Engineer Intern", "Data Science Intern", "Mathematician Intern"]
    for prefix in ("Human Resources Specialist", "Logistics Management Specialist"):
        title = by_title(postings, prefix)["PositionTitle"]
        assert not any(title_matches_role(title, role) for role in roles), title
