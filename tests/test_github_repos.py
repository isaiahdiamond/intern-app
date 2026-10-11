"""The eight repo sources, driven from the saved real files.

Every repo gets one fixture, and these tests are the spec for the three README
column layouts and the shared JSON schema. No network, no LLM.
"""

import json
from pathlib import Path

import pytest

from intern_app import db
from intern_app.sources import github_repos as gh
from intern_app.sources.ats_links import board_and_slug, known_boards, remember_board
from intern_app.sources.us_filter import is_us_or_remote

FIXTURES = Path(__file__).parent / "fixtures"


def fixture_for(repo: gh.Repo) -> Path:
    stem = repo.name.replace("/", "__").lower()
    return FIXTURES / (f"{stem}.json" if repo.kind == "json" else f"{stem}.md")


def test_every_repo_has_a_saved_fixture():
    """CLAUDE.md requires one real saved response per source."""
    for repo in gh.REPOS:
        assert fixture_for(repo).exists(), f"no fixture for {repo.name}"


@pytest.mark.parametrize("repo", gh.REPOS, ids=lambda r: r.name)
def test_every_repo_parses_to_usable_rows(repo):
    path = fixture_for(repo)
    if repo.kind == "json":
        rows = gh.parse_json_listings(json.loads(path.read_text()))
    else:
        rows = gh.parse_readme(path.read_text(), repo)

    assert rows, f"{repo.name} parsed to nothing"
    with_urls = [row for row in rows if row["url"].startswith("http")]
    # Most rows must carry an apply link, or the column layout has drifted.
    assert len(with_urls) > len(rows) * 0.8, (
        f"{repo.name}: only {len(with_urls)}/{len(rows)} linked"
    )
    for row in rows:
        assert row["title"]
        assert row["company"]


def test_closed_json_listings_are_skipped():
    """`active: false` means the repo has closed the listing."""
    path = fixture_for(gh.REPOS[0])
    payload = json.loads(path.read_text())
    closed = [item for item in payload if not item.get("active")]
    assert closed, "fixture should contain closed entries to exercise this"

    titles = {row["title"] for row in gh.parse_json_listings(payload)}
    for item in closed:
        assert gh.clean_cell(str(item["title"])) not in titles or any(
            other.get("active") and other["title"] == item["title"] for other in payload
        )


def test_speedyapply_handles_both_column_layouts():
    """It publishes a six-column table with Salary and a five-column one
    without, which moves the apply link. Indexing a fixed column dropped 656 of
    772 rows."""
    repo = next(r for r in gh.REPOS if r.kind == "speedyapply")
    rows = gh.parse_readme(fixture_for(repo).read_text(), repo)

    linked = [row for row in rows if row["url"].startswith("http")]
    assert len(linked) > len(rows) * 0.9


def test_invisible_characters_are_stripped():
    """One repo embeds a zero-width space inside titles."""
    assert gh.clean_cell("Cybersecur​ity Engineer Intern") == "Cybersecurity Engineer Intern"


def test_markup_and_emoji_come_out_of_cells():
    assert gh.clean_cell('<a href="https://x.com"><strong>Stripe</strong></a>') == "Stripe"
    assert gh.clean_cell("Workday ✓") == "Workday"
    assert (
        gh.clean_cell("[Software Engineer Intern](https://x.com/job)") == "Software Engineer Intern"
    )


def test_apply_link_skips_the_company_website():
    cells = [
        ' <a href="https://www.arcesium.com"><strong>Arcesium</strong></a> ',
        " Software Engineer Intern ",
        " New York City, NY ",
        ' <a href="https://job-boards.greenhouse.io/arcesiumllc/jobs/5257176007">apply</a> ',
        " 0d ",
    ]
    assert gh.apply_link(cells) == "https://job-boards.greenhouse.io/arcesiumllc/jobs/5257176007"


def test_repo_listings_are_never_full_text():
    """These are lists, not postings, so none may reach requirement extraction."""
    listing = gh.to_listing(
        {
            "title": "SWE Intern",
            "company": "Acme",
            "location": "Austin, TX",
            "url": "https://x.com/job",
            "posted_at": "2026-10-01",
        },
        "SimplifyJobs/Summer2027-Internships",
    )
    assert listing["full_text"] is False
    assert listing["description"] == ""
    assert listing["source"] == "github_repos:simplifyjobs"


def test_dedupe_is_on_company_title_and_location():
    """The same opening appears in several repos under different apply links,
    so the url cannot be the key."""
    one = {"company": "Stripe", "title": "SWE Intern", "location": "NYC", "url": "https://a"}
    two = {"company": "stripe", "title": "swe intern", "location": "nyc", "url": "https://b"}
    assert gh.dedupe_key(one) == gh.dedupe_key(two)


@pytest.mark.parametrize(
    ("location", "keep"),
    [
        ("Austin, TX", True),
        ("Washington, DC +1", True),
        ("Remote", True),
        ("", True),
        ("Singapore", False),
        ("London, United Kingdom +4", False),
        ("Bellevue, Australia +3", False),
        ("Remote - India", False),
        ("Toronto, Canada", False),
        ("Remote in Berlin", False),
        ("Munich, DE", False),
    ],
)
def test_us_and_remote_only(location, keep):
    assert is_us_or_remote(location) is keep


@pytest.mark.parametrize(
    "location",
    [
        "Milwaukee, WI",
        "Waukegan, IL",
        "Tukwila, WA",
        "Indianapolis, IN",
        "Albuquerque, New Mexico",
        "New York",
        "New York City",
        "San Francisco",
        "Seattle",
        "North Carolina",
        "Georgia",
        "US",
    ],
)
def test_real_us_locations_are_never_dropped(location):
    """Matching markers as substrings killed Milwaukee on "uk", Indianapolis on
    "india" and every New Mexico role on "mexico"; missing multi-word state
    names killed New York."""
    assert is_us_or_remote(location) is True


@pytest.mark.parametrize(
    ("location", "keep"),
    [
        ("Dublin, OH", True),
        ("Paris, TX", True),
        ("Athens, GA", True),
        ("Vienna, VA", True),
        ("Dublin, Ireland", False),
        ("Paris, France", False),
        ("Athens, Greece", False),
        ("Tbilisi, Georgia", False),
    ],
)
def test_cities_that_exist_on_both_sides_of_the_atlantic(location, keep):
    """A foreign city sharing a US town's name is not a marker on its own: it
    needs the country name, which these lists almost always carry."""
    assert is_us_or_remote(location) is keep


def test_a_closed_readme_row_is_skipped():
    assert gh.is_closed("| Acme | SWE Intern 🔒 | Austin, TX |") is True
    assert gh.is_closed("| Acme | SWE Intern | Austin, TX |") is False


def test_an_apply_link_teaches_us_a_board(conn):
    """Boards are discovered from links, never curated by hand."""
    remember_board(conn, "https://job-boards.greenhouse.io/arcesiumllc/jobs/123", "Arcesium")
    remember_board(conn, "https://jobs.lever.co/ramp/abc", "Ramp")
    remember_board(conn, "https://careers.example.com/job/1", "Example")

    boards = {(row["board"], row["slug"]) for row in known_boards(conn)}
    assert boards == {("greenhouse", "arcesiumllc"), ("lever", "ramp")}


def test_the_same_board_is_only_learned_once(conn):
    remember_board(conn, "https://jobs.ashbyhq.com/linear/a", "Linear")
    remember_board(conn, "https://jobs.ashbyhq.com/linear/b", "Linear")

    assert len(known_boards(conn)) == 1


def test_a_non_ats_link_teaches_us_nothing():
    assert board_and_slug("https://careers.dovercorporation.com/job/Cincinnati") is None


def test_storing_repo_listings_records_their_boards(conn):
    """Board discovery is a side effect of ordinary collection."""
    rows = gh.parse_json_listings(json.loads(fixture_for(gh.REPOS[0]).read_text()))
    for row in rows:
        if row["url"]:
            remember_board(conn, row["url"], row["company"])

    db.upsert_listings(conn, [gh.to_listing(r, "x/y") for r in rows if r["url"]])
    assert conn.execute("SELECT COUNT(*) FROM listings").fetchone()[0] > 0


def test_resumax_rows_find_the_apply_link_not_the_marketing_link():
    """Its company cell links to resumax.ai and its Tailor cell is a marketing
    link, so only the Apply cell holds the real board url."""
    repo = next(r for r in gh.REPOS if r.kind == "resumax")
    rows = gh.parse_readme(fixture_for(repo).read_text(), repo)

    assert rows
    linked = [row for row in rows if row["url"].startswith("http")]
    assert len(linked) > len(rows) * 0.9
    assert not any("resumax.ai" in row["url"] for row in linked)


def test_eu_hosted_greenhouse_boards_are_recognised():
    """resumax lists IMC on job-boards.eu.greenhouse.io, which the original
    pattern missed."""
    assert board_and_slug("https://job-boards.eu.greenhouse.io/imc/jobs/123") == (
        "greenhouse",
        "imc",
    )


@pytest.mark.parametrize(
    ("cell", "expected"),
    [
        ("0d", "2026-10-10"),
        ("3d", "2026-10-07"),
        ("2mo", "2026-08-11"),
        ("Oct 09, 2026", "2026-10-09"),
        ("Oct 10", "2026-10-10"),
        # A December row read in October belongs to the previous year.
        ("Dec 15", "2025-12-15"),
        ("", ""),
        ("garbage", ""),
    ],
)
def test_posted_dates_are_read_from_the_age_column(cell, expected):
    """Three formats appear across these repos. Without reading them, 995
    listings had no date and the posted-within filter could not see them."""
    from datetime import date

    assert gh.posted_date(cell, date(2026, 10, 10)) == expected


@pytest.mark.parametrize("repo", [r for r in gh.REPOS if r.kind != "json"], ids=lambda r: r.name)
def test_every_readme_repo_yields_dates(repo):
    rows = gh.parse_readme(fixture_for(repo).read_text(), repo)
    dated = [row for row in rows if row["posted_at"]]
    assert len(dated) > len(rows) * 0.8, f"{repo.name}: only {len(dated)}/{len(rows)} dated"


def test_the_underclassmen_repo_uses_the_shared_json_schema():
    """It publishes both a listings.json and a README. The JSON wins, per the
    source rule, and its schema matches the other JSON repos even though it
    carries extra fields of its own (target_year, opportunity_type)."""
    repo = next(r for r in gh.REPOS if "underclassmen" in r.name)
    assert repo.kind == "json"

    payload = json.loads(fixture_for(repo).read_text())
    assert any("target_year" in entry for entry in payload)

    rows = gh.parse_json_listings(payload)
    assert rows
    for row in rows:
        assert row["title"]
        assert row["company"]
        assert row["url"].startswith("http")
