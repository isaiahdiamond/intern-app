import pytest

from intern_app import db
from intern_app.sources.base import normalize


@pytest.fixture
def conn():
    """An in-memory database with the schema applied. No file, no network."""
    connection = db.connect(":memory:")
    yield connection
    connection.close()


@pytest.fixture
def listing():
    """A factory for valid listings, so tests vary only what they care about."""

    def make(url="https://example.com/jobs/1", *, full_text=True, source="muse", **over):
        fields = {
            "title": "Software Engineering Intern",
            "company": "Example Co",
            "location": "Boston, MA",
            "url": url,
            "description": "We want Python and SQL." if full_text else "",
            "posted_at": "2026-10-01",
            "source": source,
            "full_text": full_text,
        }
        fields.update(over)
        return normalize(**fields)

    return make
