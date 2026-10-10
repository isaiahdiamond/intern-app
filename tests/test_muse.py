"""The Muse source, driven entirely from the saved real response.

Title matching is the main risk in this source: too loose floods the board with
unrelated jobs, too strict hides good ones. A Muse category is broad — Software
Engineering alone holds 874 internships — so these cases are the filter's spec.
"""

import json
from pathlib import Path

import pytest

from intern_app.sources import muse

FIXTURE = Path(__file__).parent / "fixtures" / "muse_search.json"


@pytest.fixture(scope="module")
def muse_response():
    return json.loads(FIXTURE.read_text())


def test_the_fixture_is_a_real_response(muse_response):
    assert muse_response["page_count"] > 0
    assert len(muse_response["results"]) == 20


def test_a_real_job_normalizes_to_the_contract(muse_response):
    jobs = {job["name"]: job for job in muse_response["results"]}
    job = jobs["Spring 2027 Software Engineering Internship/Co-op"]

    listing = muse.to_listing(job)

    assert listing["company"] == "SpaceX"
    assert listing["source"] == "muse"
    assert listing["full_text"] is True
    assert listing["url"].startswith("https://www.themuse.com/jobs/spacex/")
    assert "Brownsville, TX" in listing["location"]
    assert listing["posted_at"].startswith("2026-09-30")
    # contents is HTML; the stored description must be readable text.
    assert "<div>" not in listing["description"]
    assert "<p>" not in listing["description"]
    assert len(listing["description"]) > 500


def test_every_fixture_job_normalizes_without_error(muse_response):
    for job in muse_response["results"]:
        listing = muse.to_listing(job)
        assert listing["url"]
        assert listing["full_text"] is True


@pytest.mark.parametrize(
    ("title", "role"),
    [
        ("Spring 2027 Software Engineering Internship/Co-op", "Software Engineer Intern"),
        ("Software Engineer Intern (Ads Interface) - 2027 Summer", "Software Engineer Intern"),
        ("New Graduate Engineer, Software (Starship)", "Software Engineer Intern"),
        # developer and engineer are the same opening
        ("Software Developer Intern", "Software Engineer Intern"),
        # hyphenation and casing must not matter
        ("Back-End Engineer Intern", "Backend Engineer Intern"),
        # ML written as AI still matches a machine learning role
        ("AI Infrastructure Engineer Intern", "Machine Learning Intern"),
        ("Machine Learning Engineer Intern (Global E-Commerce)", "Machine Learning Intern"),
        # scientist vs science is a stem away
        ("Summer Associate Internship (Data Scientist)", "Data Science Intern"),
        ("Junior Data Scientist", "Data Science Intern"),
        # a single-word role matched as a whole word
        ("Actuarial Analyst Intern", "Actuarial Intern"),
    ],
)
def test_titles_that_must_match(title, role):
    assert muse.title_matches_role(title, role) is True


@pytest.mark.parametrize(
    ("title", "role"),
    [
        # a different engineering discipline
        ("Mechanical Engineer Intern", "Software Engineer Intern"),
        ("PCB Technician (Starlink)", "Software Engineer Intern"),
        # data roles must not swallow each other
        ("Data Engineer Intern", "Data Analyst Intern"),
        # the single-word rule: Product must not match Production
        ("Production Engineer Intern", "Product Intern"),
        # nothing in common
        ("LPN - Inpatient", "Software Engineer Intern"),
        ("Retail Sales Merchander", "Data Science Intern"),
    ],
)
def test_titles_that_must_not_match(title, role):
    assert muse.title_matches_role(title, role) is False


def test_role_to_category_uses_whole_words():
    """A substring match sent anything containing "it" to Computer and IT."""
    assert muse.categories_for_role("IT Intern") == ("Computer and IT",)
    assert "Computer and IT" not in muse.categories_for_role("Digital Marketing Intern")
    assert muse.categories_for_role("Production Engineer Intern") != ("Product Management",)


def test_role_to_category_prefers_the_longest_match():
    assert muse.categories_for_role("Quantitative Research Intern") == (
        "Data and Analytics",
        "Accounting and Finance",
    )
    assert muse.categories_for_role("Research Intern") == ("Science and Engineering",)


def test_an_unknown_role_maps_to_no_category():
    """No category means no request, rather than a guess that returns nothing."""
    assert muse.categories_for_role("Underwater Welding Intern") == ()


def test_each_category_and_level_is_requested_once_not_once_per_role():
    """Fetching per role re-read the same pages and burnt the daily budget."""
    roles = [
        "Software Engineer Intern",
        "Backend Engineer Intern",
        "Full Stack Engineer Intern",
        "Machine Learning Intern",
    ]

    queries = muse._queries_for(roles, None)

    assert len(queries) == len(set(queries))
    software = [q for q in queries if q[0] == "Software Engineering"]
    # One per level, not one per role.
    assert len(software) == len(muse.LEVELS)


def test_both_internship_and_new_grad_levels_are_queried():
    """New grad roles come from the Entry Level filter."""
    levels = {level for _, level, _ in muse._queries_for(["Software Engineer Intern"], None)}
    assert levels == {"Internship", "Entry Level"}


def test_fetch_drops_listings_outside_the_us(conn, monkeypatch):
    """The Muse is worldwide, so 44 Singapore roles reached the database before
    this check existed. This fails if the filter is removed."""
    import httpx

    from intern_app import config

    monkeypatch.setenv("MUSE_API_KEY", "not-a-real-key")
    config.settings.cache_clear()

    page = {
        "page_count": 1,
        "results": [
            {
                "name": "Software Engineer Intern",
                "company": {"name": "Here Inc"},
                "locations": [{"name": "Austin, TX"}],
                "refs": {"landing_page": "https://themuse.com/jobs/here"},
                "contents": "<p>We want Python.</p>",
                "publication_date": "2026-10-01T00:00:00Z",
            },
            {
                "name": "Software Engineer Intern",
                "company": {"name": "There Ltd"},
                "locations": [{"name": "Singapore"}],
                "refs": {"landing_page": "https://themuse.com/jobs/there"},
                "contents": "<p>We want Python.</p>",
                "publication_date": "2026-10-01T00:00:00Z",
            },
        ],
    }

    def fake_get(self, url, **kwargs):
        return httpx.Response(200, json=page, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.Client, "get", fake_get)

    found = muse.fetch_muse(conn, ["Software Engineer Intern"], max_pages=1)

    assert [listing["company"] for listing in found] == ["Here Inc"]


def test_ai_spelled_out_matches_a_machine_learning_role():
    """ "Artificial Intelligence Co-Op/Intern" matched no role at all until the
    spelled-out form was aliased alongside "ai"."""
    assert muse.title_matches_role(
        "Artificial Intelligence Co-Op/Intern - Spring 2027", "Machine Learning Intern"
    )
