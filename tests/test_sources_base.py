"""The source contract is the spine of the project, so it gets real tests."""

import pytest

from intern_app.sources.base import LISTING_FIELDS, normalize

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


def test_normalize_returns_the_contract_keys_and_trims():
    listing = normalize(**FULL)
    assert set(listing) == set(LISTING_FIELDS)
    assert listing["title"] == "Software Engineering Intern"


def test_discovery_only_listing_drops_its_description():
    listing = normalize(**{**FULL, "full_text": False, "description": "Truncated teaser…"})
    assert listing["description"] == ""


def test_full_text_without_a_description_is_an_error():
    with pytest.raises(ValueError, match="description is empty"):
        normalize(**{**FULL, "description": "   "})


def test_missing_url_is_an_error_because_url_is_the_dedupe_key():
    with pytest.raises(ValueError, match="no url"):
        normalize(**{**FULL, "url": None})


def test_full_text_must_be_a_bool_not_a_truthy_value():
    """A truthy 1 slipping through would break the extraction gate."""
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
