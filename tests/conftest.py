import pytest

from intern_app import config, db
from intern_app.sources.base import normalize

CREDENTIALS = (
    "ANTHROPIC_API_KEY",
    "MUSE_API_KEY",
    "ADZUNA_APP_ID",
    "ADZUNA_APP_KEY",
    "USAJOBS_API_KEY",
    "USAJOBS_EMAIL",
)


@pytest.fixture(autouse=True)
def no_real_credentials(monkeypatch):
    """Blank every credential so no test depends on my own .env.

    Blank rather than deleted: `load_dotenv` does not override a variable that
    is already present, so setting it empty is what actually keeps the real key
    out. A test that wants a credential sets it itself afterwards.
    """
    for name in CREDENTIALS:
        monkeypatch.setenv(name, "")
    config.settings.cache_clear()
    yield
    config.settings.cache_clear()


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
