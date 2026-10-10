"""The board: which listings to show, in what order, and their status.

Ordering is the profile's industry ranking first, then newest. Industry comes
from the company, and a company with no industry — or one in an industry the
user did not rank — sorts last rather than being hidden, because a good role at
a company in a fifth-choice industry is still worth seeing.
"""

from __future__ import annotations

import sqlite3

from intern_app.db import utcnow

STATUSES = ("new", "saved", "applied", "interviewing", "rejected", "offer", "hidden")

# Statuses that mean "I am doing something about this", which is the tracker.
ACTIVE = ("saved", "applied", "interviewing", "rejected", "offer")

# Any industry not in the profile's ranking sorts after every ranked one.
UNRANKED = 999

SELECT_LISTINGS = """
    SELECT l.id, l.title, l.company, l.location, l.url, l.posted_at, l.source,
           l.full_text, l.first_seen,
           COALESCE(c.industry, '') AS industry,
           COALESCE(pi.rank, :unranked) AS industry_rank,
           COALESCE(t.status, 'new') AS status,
           COALESCE(t.notes, '') AS notes
    FROM listings l
    LEFT JOIN companies c ON c.name = l.company
    LEFT JOIN profile_industries pi ON pi.industry = c.industry
    LEFT JOIN tracker t ON t.listing_id = l.id
"""


def list_new(
    conn: sqlite3.Connection,
    *,
    industry: str = "",
    days: int = 0,
    limit: int = 200,
) -> list[sqlite3.Row]:
    """Listings I have not acted on yet, best-matching industry first.

    `days` limits to recently posted when set, which matters because a source
    will happily return a posting from last year.
    """
    where = ["COALESCE(t.status, 'new') = 'new'"]
    params: dict[str, object] = {"unranked": UNRANKED, "limit": limit}

    if industry:
        where.append("COALESCE(c.industry, '') = :industry")
        params["industry"] = industry
    if days:
        where.append("l.posted_at >= date('now', :cutoff)")
        params["cutoff"] = f"-{int(days)} days"

    sql = f"""
        {SELECT_LISTINGS}
        WHERE {" AND ".join(where)}
        ORDER BY industry_rank, l.posted_at DESC, l.id DESC
        LIMIT :limit
    """
    return conn.execute(sql, params).fetchall()


def search_listings(
    conn: sqlite3.Connection,
    *,
    text: str = "",
    industry: str = "",
    status: str = "",
    limit: int = 200,
) -> list[sqlite3.Row]:
    """Every stored listing, filtered. This is what the Search tab reads."""
    where = ["1 = 1"]
    params: dict[str, object] = {"unranked": UNRANKED, "limit": limit}

    if text:
        where.append("(l.title LIKE :text OR l.company LIKE :text OR l.location LIKE :text)")
        params["text"] = f"%{text}%"
    if industry:
        where.append("COALESCE(c.industry, '') = :industry")
        params["industry"] = industry
    if status:
        where.append("COALESCE(t.status, 'new') = :status")
        params["status"] = status

    sql = f"""
        {SELECT_LISTINGS}
        WHERE {" AND ".join(where)}
        ORDER BY industry_rank, l.posted_at DESC, l.id DESC
        LIMIT :limit
    """
    return conn.execute(sql, params).fetchall()


def list_tracked(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Everything I have acted on, grouped by status in pipeline order."""
    sql = f"""
        {SELECT_LISTINGS}
        WHERE t.status IN ({",".join(f"'{name}'" for name in ACTIVE)})
        ORDER BY CASE t.status
                     WHEN 'offer' THEN 1
                     WHEN 'interviewing' THEN 2
                     WHEN 'applied' THEN 3
                     WHEN 'saved' THEN 4
                     ELSE 5
                 END,
                 t.updated_at DESC
    """
    return conn.execute(sql, {"unranked": UNRANKED}).fetchall()


def set_status(conn: sqlite3.Connection, listing_id: int, status: str) -> None:
    """Move a listing to a status and record the change in the history."""
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}, got {status!r}")

    now = utcnow()
    conn.execute("BEGIN")
    try:
        conn.execute(
            """
            INSERT INTO tracker (listing_id, status, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (listing_id) DO UPDATE SET
                status = excluded.status,
                updated_at = excluded.updated_at
            """,
            (listing_id, status, now, now),
        )
        conn.execute(
            "INSERT INTO tracker_history (listing_id, status, changed_at) VALUES (?, ?, ?)",
            (listing_id, status, now),
        )
    except Exception:
        conn.execute("ROLLBACK")
        raise
    conn.execute("COMMIT")


def history_for(conn: sqlite3.Connection, listing_id: int) -> list[sqlite3.Row]:
    """Every status this listing has been through, oldest first."""
    return conn.execute(
        "SELECT status, changed_at FROM tracker_history WHERE listing_id = ? ORDER BY id",
        (listing_id,),
    ).fetchall()


def status_counts(conn: sqlite3.Connection) -> dict[str, int]:
    """How many listings sit at each status, for the tab badges."""
    rows = conn.execute("SELECT status, COUNT(*) AS n FROM tracker GROUP BY status").fetchall()
    counts = {row["status"]: row["n"] for row in rows}
    counts["new"] = conn.execute(
        """
        SELECT COUNT(*) FROM listings l
        LEFT JOIN tracker t ON t.listing_id = l.id
        WHERE COALESCE(t.status, 'new') = 'new'
        """
    ).fetchone()[0]
    return counts


def known_industries(conn: sqlite3.Connection) -> list[str]:
    """Industries actually present in the stored listings, for the filter."""
    rows = conn.execute(
        """
        SELECT DISTINCT c.industry FROM listings l
        JOIN companies c ON c.name = l.company
        WHERE c.industry IS NOT NULL AND c.industry <> ''
        ORDER BY c.industry
        """
    ).fetchall()
    return [row["industry"] for row in rows]
