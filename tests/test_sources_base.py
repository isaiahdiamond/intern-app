"""The source contract is the spine of the project, so it gets real tests."""

import pytest

from intern_app.sources.base import LISTING_FIELDS, clean, normalize, strip_html

FULL = {
    "title": "  Software Engineering Intern ",
    "company": "Example Co",
    "location": "Boston, MA",
    "url": "https://example.com/jobs/1",
    "description": "We want Python and SQL.",
    "posted_at": "2026-10-01",
    "source": "muse",
    "full_text": True,
}


def test_normalize_returns_exactly_the_contract_keys():
    listing = normalize(**FULL)
    assert set(listing) == set(LISTING_FIELDS)


def test_normalize_trims_whitespace():
    assert normalize(**FULL)["title"] == "Software Engineering Intern"


def test_discovery_only_listing_drops_its_description():
    listing = normalize(**{**FULL, "full_text": False, "description": "Truncated teaser…"})
    assert listing["description"] == ""
    assert listing["full_text"] is False


def test_full_text_without_a_description_is_an_error():
    with pytest.raises(ValueError, match="description is empty"):
        normalize(**{**FULL, "description": "   "})


def test_missing_url_is_an_error_because_url_is_the_dedupe_key():
    with pytest.raises(ValueError, match="no url"):
        normalize(**{**FULL, "url": None})


def test_full_text_must_be_a_bool_not_a_truthy_value():
    with pytest.raises(TypeError, match="must be a bool"):
        normalize(**{**FULL, "full_text": 1})


def test_html_descriptions_keep_their_structure():
    listing = normalize(
        **{
            **FULL,
            "description": "<p>Requirements:</p><ul><li>Python</li><li>SQL &amp; dbt</li></ul>",
            "is_html": True,
        }
    )
    assert listing["description"] == "Requirements:\n\n- Python\n- SQL & dbt"


def test_strip_html_on_empty_input():
    assert strip_html("") == ""


def test_clean_coerces_none_and_numbers():
    assert clean(None) == ""
    assert clean(42) == "42"
