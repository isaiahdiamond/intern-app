"""Preferences about the app itself, as opposed to the job search.

Kept as key and value so that adding a preference needs no migration. The
module is named `settings_store` because `config.settings` already means the
environment, and two things called settings in one codebase is one too many.
"""

from __future__ import annotations

import sqlite3

from intern_app.db import utcnow

# Every preference the app knows, with the value used when none is stored.
# A key absent from here is rejected, so a typo in a request cannot quietly
# write a setting that nothing ever reads.
DEFAULTS = {
    "background": "meadow",
}

# The backgrounds Settings offers. Kept here as well as in the front end's
# manifest so the API can refuse a value that has no image behind it.
BACKGROUNDS = (
    "meadow",
    "coast",
    "dunes",
    "alpine",
    "forest",
    "clouds",
    "snow",
    "dusk",
    "silk",
)


def read_settings(conn: sqlite3.Connection) -> dict[str, str]:
    """Every preference, with defaults filling in whatever was never set."""
    stored = {row["key"]: row["value"] for row in conn.execute("SELECT key, value FROM settings")}
    return {key: stored.get(key, fallback) for key, fallback in DEFAULTS.items()}


def save_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    """Store one preference, replacing any earlier value."""
    if key not in DEFAULTS:
        raise ValueError(f"unknown setting {key!r}, expected one of {sorted(DEFAULTS)}")
    if key == "background" and value not in BACKGROUNDS:
        raise ValueError(f"unknown background {value!r}, expected one of {list(BACKGROUNDS)}")
    conn.execute(
        """
        INSERT INTO settings (key, value, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT (key) DO UPDATE SET
            value = excluded.value,
            updated_at = excluded.updated_at
        """,
        (key, value, utcnow()),
    )
