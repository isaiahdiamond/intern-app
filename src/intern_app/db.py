"""SQLite storage: listings, API-call accounting, and the LLM call log.

One connection helper and a small set of functions. Callers pass a connection so
tests can run against `:memory:` and nothing reaches for global state.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from intern_app.config import settings
from intern_app.llm import pricing
from intern_app.sources.base import Listing

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def utcnow() -> str:
    """Timestamps are ISO 8601 UTC strings, which sort lexicographically."""
    return datetime.now(UTC).isoformat(timespec="seconds")


def connect(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Open a connection and apply the schema.

    Pass `":memory:"` in tests. A file path has its parent directory created,
    since the default database lives in a gitignored `data/`.
    """
    target = db_path if db_path is not None else settings().db_path
    if target != ":memory:":
        Path(target).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_PATH.read_text())
    # schema.sql sets this too, but a PRAGMA inside executescript's transaction
    # is ignored, so the ON DELETE CASCADE clauses would never fire.
    conn.execute("PRAGMA foreign_keys = ON")
    add_missing_columns(conn)
    return conn


# Columns added to a table that already exists in a database out in the world.
# `CREATE TABLE IF NOT EXISTS` does nothing for a table that is already there,
# so a new column has to be added by hand or the live database never gets it.
ADDED_COLUMNS = (("profile", "education", "TEXT NOT NULL DEFAULT ''"),)


def add_missing_columns(conn: sqlite3.Connection) -> None:
    """Add any column the schema has gained since this database was created."""
    for table, column, definition in ADDED_COLUMNS:
        existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}
        if column not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


# --- listings ---------------------------------------------------------------


def upsert_listings(conn: sqlite3.Connection, listings: Iterable[Listing]) -> tuple[int, int]:
    """Insert new listings and refresh `last_seen` on ones already stored.

    Returns `(inserted, updated)`. Dedupe is on `url`. A repeat sighting keeps
    the original `first_seen` so "new since yesterday" stays answerable, and
    refreshes the content fields, because a posting can be edited after it goes
    up.
    """
    inserted = updated = 0
    now = utcnow()
    for listing in listings:
        existing = conn.execute(
            "SELECT 1 FROM listings WHERE url = ?", (listing["url"],)
        ).fetchone()
        conn.execute(
            """
            INSERT INTO listings
                (url, title, company, location, description, posted_at, source,
                 full_text, first_seen, last_seen)
            VALUES (:url, :title, :company, :location, :description, :posted_at,
                    :source, :full_text, :now, :now)
            ON CONFLICT (url) DO UPDATE SET
                title       = excluded.title,
                company     = excluded.company,
                location    = excluded.location,
                posted_at   = excluded.posted_at,
                last_seen   = excluded.last_seen,
                -- Never let a later discovery-only sighting blank out a
                -- description we already have the full text of.
                description = CASE
                    WHEN excluded.full_text = 1 THEN excluded.description
                    ELSE listings.description
                END,
                full_text   = CASE
                    WHEN excluded.full_text = 1 THEN 1
                    ELSE listings.full_text
                END
            """,
            {**listing, "full_text": int(listing["full_text"]), "now": now},
        )
        # Counted from the pre-write lookup. `cursor.rowcount` cannot tell the
        # two apart (SQLite reports 1 for an insert and 1 for an upsert update),
        # and comparing first_seen to last_seen fails when a re-sight lands in
        # the same second as the insert.
        remember_company(conn, listing["company"])

        if existing is None:
            inserted += 1
        else:
            updated += 1
    return inserted, updated


def listings_needing_extraction(
    conn: sqlite3.Connection,
    limit: int = 50,
    *,
    prompt_name: str = "extract_skills",
) -> list[sqlite3.Row]:
    """Listings eligible for skill extraction: full text, not yet extracted.

    The `full_text = 1` filter is the rule from CLAUDE.md, enforced in SQL so no
    caller can route a truncated description to the extractor. Matching on
    `prompt_name` matters because later phases log other prompts against the same
    listing, and those must not count as an extraction.
    """
    return conn.execute(
        """
        SELECT l.* FROM listings l
        WHERE l.full_text = 1
          AND NOT EXISTS (
              SELECT 1 FROM llm_calls c
              WHERE c.listing_id = l.id
                AND c.ok = 1
                AND c.prompt_name = ?
          )
        ORDER BY l.first_seen DESC
        LIMIT ?
        """,
        (prompt_name, limit),
    ).fetchall()


# --- API call accounting ----------------------------------------------------


def _safe_endpoint(endpoint: str) -> str:
    """Drop the query string and fragment before anything is stored.

    Adzuna, The Muse, and USAJobs all pass credentials as query parameters, so a
    caller handing us a full request URL would write a key into the database.
    Only the scheme, host, and path survive.
    """
    return urlsplit(endpoint)._replace(query="", fragment="").geturl()


def record_api_call(
    conn: sqlite3.Connection,
    *,
    source: str,
    endpoint: str = "",
    status_code: int | None = None,
    ok: bool = True,
    error: str = "",
) -> None:
    """Record one outbound call. Write this for failures too — they spend quota.

    `endpoint` is stored with its query string stripped, so passing a full
    request URL is safe. Keep `error` free of credentials for the same reason —
    prefer the exception class and status code over `str(exc)` on a URL.
    """
    conn.execute(
        """
        INSERT INTO api_calls (source, endpoint, called_at, status_code, ok, error)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (source, _safe_endpoint(endpoint), utcnow(), status_code, int(ok), error),
    )


def calls_since(conn: sqlite3.Connection, source: str, since: datetime) -> int:
    """How many calls `source` has made since `since`."""
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM api_calls WHERE source = ? AND called_at >= ?",
        (source, since.isoformat(timespec="seconds")),
    ).fetchone()
    return int(row["n"])


def calls_in_last(conn: sqlite3.Connection, source: str, *, days: int = 0, hours: int = 0) -> int:
    """How many calls `source` has made in a trailing window."""
    return calls_since(conn, source, datetime.now(UTC) - timedelta(days=days, hours=hours))


def last_call_at(conn: sqlite3.Connection, source: str) -> str:
    """Timestamp of the most recent call, or "" if the source never ran.

    Board endpoints are polled at most every few hours; this is how a source
    knows whether enough time has passed.
    """
    row = conn.execute(
        "SELECT MAX(called_at) AS t FROM api_calls WHERE source = ?", (source,)
    ).fetchone()
    return row["t"] or ""


# --- LLM call log -----------------------------------------------------------


def record_llm_call(
    conn: sqlite3.Connection,
    *,
    prompt_name: str,
    model: str,
    listing_id: int | None = None,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_read_tokens: int = 0,
    cache_write_tokens: int = 0,
    request_id: str = "",
    input_text: str = "",
    output_text: str = "",
    ok: bool = True,
    error: str = "",
) -> int:
    """Record one Claude call and return its row id.

    Cost is computed here from `model` and the token counts rather than accepted
    as an argument: CLAUDE.md requires every call to carry a computed cost, and a
    caller-supplied figure can silently be zero. `pricing.cost_usd` raises on an
    unpriced model, so a wrong cost cannot reach the log.
    """
    cost = pricing.cost_usd(
        model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_tokens=cache_read_tokens,
        cache_write_tokens=cache_write_tokens,
    )
    cursor = conn.execute(
        """
        INSERT INTO llm_calls
            (prompt_name, model, listing_id, called_at, input_tokens, output_tokens,
             cache_read_tokens, cache_write_tokens, cost_usd, request_id,
             input_text, output_text, ok, error)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            prompt_name,
            model,
            listing_id,
            utcnow(),
            input_tokens,
            output_tokens,
            cache_read_tokens,
            cache_write_tokens,
            cost,
            request_id,
            input_text,
            output_text,
            int(ok),
            error,
        ),
    )
    return int(cursor.lastrowid or 0)


def llm_spend(conn: sqlite3.Connection, *, days: int | None = None) -> dict[str, Any]:
    """Total calls, tokens, and dollars spent, optionally over a trailing window."""
    where = ""
    params: tuple[Any, ...] = ()
    if days is not None:
        where = "WHERE called_at >= ?"
        params = ((datetime.now(UTC) - timedelta(days=days)).isoformat(timespec="seconds"),)
    row = conn.execute(
        f"""
        SELECT COUNT(*)                     AS calls,
               COALESCE(SUM(input_tokens),  0) AS input_tokens,
               COALESCE(SUM(output_tokens), 0) AS output_tokens,
               COALESCE(SUM(cost_usd),      0.0) AS cost_usd
        FROM llm_calls {where}
        """,  # noqa: S608 — `where` is a literal chosen above, never caller input
        params,
    ).fetchone()
    return dict(row)


def remember_company(conn: sqlite3.Connection, name: str) -> None:
    """Make sure a company has a row, so it can be classified later."""
    if name.strip():
        conn.execute("INSERT OR IGNORE INTO companies (name) VALUES (?)", (name.strip(),))


def companies_needing_industry(conn: sqlite3.Connection) -> list[str]:
    """Companies we hold listings for that have no industry yet."""
    # Driven from `listings`, not from `companies`: a listing stored before this
    # table existed has no company row, and deriving the list from the listings
    # themselves means no backfill step can be forgotten.
    rows = conn.execute(
        """
        SELECT DISTINCT l.company AS name
        FROM listings l
        LEFT JOIN companies c ON c.name = l.company
        WHERE l.company <> '' AND (c.industry IS NULL)
        ORDER BY l.company
        """
    ).fetchall()
    return [row["name"] for row in rows]


def set_company_industry(conn: sqlite3.Connection, name: str, industry: str) -> None:
    """Store a company's industry, creating its row if this is the first time."""
    conn.execute(
        """
        INSERT INTO companies (name, industry, classified_at) VALUES (?, ?, ?)
        ON CONFLICT (name) DO UPDATE SET
            industry = excluded.industry,
            classified_at = excluded.classified_at
        """,
        (name.strip(), industry, utcnow()),
    )


def listings_needing_clean_title(conn: sqlite3.Connection, limit: int = 0) -> list[sqlite3.Row]:
    """Listings whose title has not been read yet, newest first."""
    sql = """
        SELECT l.id, l.title
        FROM listings l
        LEFT JOIN listing_details d ON d.listing_id = l.id
        WHERE d.listing_id IS NULL
        ORDER BY l.first_seen DESC, l.id DESC
    """
    if limit:
        return conn.execute(sql + " LIMIT ?", (limit,)).fetchall()
    return conn.execute(sql).fetchall()


def set_listing_detail(
    conn: sqlite3.Connection,
    *,
    listing_id: int,
    clean_title: str,
    level: str,
    education: str,
    term: str,
) -> None:
    """Store how a title reads, replacing any earlier reading."""
    conn.execute(
        """
        INSERT INTO listing_details
            (listing_id, clean_title, level, education, term, cleaned_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT (listing_id) DO UPDATE SET
            clean_title = excluded.clean_title,
            level = excluded.level,
            education = excluded.education,
            term = excluded.term,
            cleaned_at = excluded.cleaned_at
        """,
        (listing_id, clean_title, level, education, term, utcnow()),
    )


def source_counts(conn: sqlite3.Connection) -> Sequence[sqlite3.Row]:
    """Listings per source, for the CLI status view."""
    return conn.execute(
        """
        SELECT source,
               COUNT(*)                        AS listings,
               SUM(full_text)                  AS with_full_text,
               MAX(last_seen)                  AS last_seen
        FROM listings
        GROUP BY source
        ORDER BY listings DESC
        """
    ).fetchall()
