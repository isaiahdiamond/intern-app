"""Adzuna, driven from the saved real response.

The important property here is that the API key never reaches storage: Adzuna
returns it inside every redirect URL as `utm_source`. The fixture keeps that
shape with a placeholder standing in for the real id.
"""

import json
from pathlib import Path

import pytest

from intern_app.sources import adzuna

FIXTURE = Path(__file__).parent / "fixtures" / "adzuna_search.json"
PLACEHOLDER = "APPIDPLACEHOLDER"


@pytest.fixture(scope="module")
def results():
    return json.loads(FIXTURE.read_text())["results"]


def test_the_fixture_is_a_real_response(results):
    assert len(results) == 10
    assert results[0]["redirect_url"].startswith("https://www.adzuna.com/details/")


def test_the_api_key_never_survives_into_a_stored_url(results):
    """Adzuna puts the app id in every redirect URL as utm_source."""
    for job in results:
        assert PLACEHOLDER in job["redirect_url"], "fixture should carry the key's position"
        listing = adzuna.to_listing(job, secrets=(PLACEHOLDER,))
        assert PLACEHOLDER not in listing["url"]


@pytest.mark.parametrize(
    "url",
    [
        f"https://www.adzuna.com/details/1?utm_medium=api&utm_source={PLACEHOLDER}",
        # The parameter name is not guaranteed to arrive lowercase.
        f"https://www.adzuna.com/details/1?UTM_SOURCE={PLACEHOLDER}",
        # A fragment survives query cleaning unless it is dropped.
        f"https://www.adzuna.com/details/1#utm_source={PLACEHOLDER}",
        f"https://www.adzuna.com/details/1?utm_source%5B%5D={PLACEHOLDER}",
        f"https://www.adzuna.com/details/1?a=b;utm_source={PLACEHOLDER}",
        # The key under some other name, or in the path.
        f"https://www.adzuna.com/details/1?x={PLACEHOLDER}",
        f"https://www.adzuna.com/{PLACEHOLDER}/ad/1",
    ],
)
def test_no_arrangement_of_the_key_gets_through(url):
    """Stripping one known parameter is a guess about where the key sits;
    checking the finished string is the guarantee."""
    cleaned = adzuna.clean_url(url, secrets=(PLACEHOLDER,))

    assert PLACEHOLDER not in cleaned


def test_a_clean_url_is_kept_intact():
    url = "https://www.adzuna.com/details/5878076196?utm_medium=api"

    assert adzuna.clean_url(url, secrets=(PLACEHOLDER,)) == url


def test_a_rejected_url_is_empty_so_the_listing_is_skipped():
    """fetch_adzuna drops listings with no url, so refusing one is enough."""
    assert adzuna.clean_url(f"https://x.com/{PLACEHOLDER}", secrets=(PLACEHOLDER,)) == ""


def test_descriptions_are_truncated_so_nothing_is_stored(results):
    """Theirs stop at 500 characters with an ellipsis. A partial posting must
    never reach requirement extraction."""
    raw = results[0]["description"]
    assert len(raw) == 500
    assert raw.rstrip().endswith(("…", "..."))

    listing = adzuna.to_listing(results[0], secrets=(PLACEHOLDER,))
    assert listing["full_text"] is False
    assert listing["description"] == ""


def test_a_real_result_normalizes(results):
    listing = adzuna.to_listing(results[0], secrets=(PLACEHOLDER,))

    assert listing["company"] == "Texas Instruments"
    assert listing["location"] == "Dallas, Texas"
    assert listing["source"] == "adzuna"
    assert len(listing["posted_at"]) == 10


def test_the_attribution_their_terms_require_is_defined():
    assert adzuna.ATTRIBUTION == "Jobs by Adzuna"
