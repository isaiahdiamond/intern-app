"""Spotting an ATS board in an apply link.

Company boards are never user-managed: a slug is learned whenever a listing's
url points at one, so every other source feeds board discovery as a side
effect of normal collection.
"""

from __future__ import annotations

import re
import sqlite3
from urllib.parse import urlsplit

from intern_app.db import utcnow

# board name -> patterns that carry the slug in an apply URL.
PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("greenhouse", re.compile(r"(?:boards|job-boards)\.greenhouse\.io/([^/?#]+)")),
    ("greenhouse", re.compile(r"greenhouse\.io/embed/job_board\?for=([^&/?#]+)")),
    ("lever", re.compile(r"jobs\.(?:eu\.)?lever\.co/([^/?#]+)")),
    ("ashby", re.compile(r"jobs\.ashbyhq\.com/([^/?#]+)")),
)

# Slugs that are a path segment of the site itself, not a company.
NOT_A_SLUG = frozenset({"embed", "job_board", "jobs", "api", "", "www"})


def board_and_slug(url: str) -> tuple[str, str] | None:
    """The (board, slug) an apply link points at, or None if it is not an ATS."""
    if not url:
        return None
    for board, pattern in PATTERNS:
        found = pattern.search(url)
        if found:
            slug = found.group(1).strip().lower()
            if slug not in NOT_A_SLUG:
                return board, slug
    return None


def remember_board(conn: sqlite3.Connection, url: str, company: str = "") -> tuple[str, str] | None:
    """Store the board behind an apply link, if there is one. Returns what it found."""
    found = board_and_slug(url)
    if found is None:
        return None

    board, slug = found
    conn.execute(
        """
        INSERT INTO ats_boards (board, slug, company, found_at) VALUES (?, ?, ?, ?)
        ON CONFLICT (board, slug) DO UPDATE SET
            company = CASE WHEN ats_boards.company = '' THEN excluded.company
                           ELSE ats_boards.company END
        """,
        (board, slug, company.strip(), utcnow()),
    )
    return found


def known_boards(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Every board discovered so far, newest first."""
    return conn.execute(
        "SELECT board, slug, company, found_at FROM ats_boards ORDER BY found_at DESC, id DESC"
    ).fetchall()


def host_of(url: str) -> str:
    """The hostname of a url, for reporting which sites listings point at."""
    return urlsplit(url).hostname or ""
