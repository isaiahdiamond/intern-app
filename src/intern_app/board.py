"""The board: which listings to show, in what order, and their status.

Ordering is the profile's industry ranking first, then newest. Industry comes
from the company, and a company with no industry — or one in an industry the
user did not rank — sorts last rather than being hidden, because a good role at
a company in a fifth-choice industry is still worth seeing.
"""

from __future__ import annotations

import sqlite3

from intern_app import db
from intern_app.db import utcnow

STATUSES = ("new", "saved", "applied", "interviewing", "rejected", "offer", "hidden")

# `hidden` is the ignore shelf: a listing the user has deliberately pushed off
# the board. It is the only status the list hides by default, because every
# other one is information the user wants while scanning — seeing "Applied"
# next to a role is how you avoid applying to it twice.
IGNORED = "hidden"

# Statuses that mean "I am doing something about this", which is the tracker.
ACTIVE = ("saved", "applied", "interviewing", "rejected", "offer")

# Any industry not in the profile's ranking sorts after every ranked one.
UNRANKED = 999

# One row per opening. The same job is sometimes posted several times under
# different urls — four SpaceX "New Graduate Engineer, Software Security" rows
# in Redmond, each with its own url hash — so the board shows one of them and
# prefers the copy that has a full description. Nothing is deleted: every url
# stays in `listings`, and the Search tab still reaches all of them.
#
# Note that the same title at a *different* location is a different opening, not
# a duplicate: RWS lists "General AI Data Annotator" in California, Dallas and
# New Jersey, and all three are real.
SELECT_LISTINGS = """
    WITH ranked_listings AS (
        SELECT l.*,
               ROW_NUMBER() OVER (
                   PARTITION BY lower(l.company), lower(l.title), lower(l.location)
                   ORDER BY l.full_text DESC, l.id
               ) AS copy_number,
               COUNT(*) OVER (
                   PARTITION BY lower(l.company), lower(l.title), lower(l.location)
               ) AS copies
        FROM listings l
    )
    SELECT l.id, l.title, l.company, l.location, l.url, l.posted_at, l.source,
           l.full_text, l.first_seen, l.copies,
           -- The raw title is kept untouched; this is what the board shows.
           COALESCE(NULLIF(d.clean_title, ''), l.title) AS display_title,
           COALESCE(d.level, '') AS level,
           COALESCE(d.education, '') AS education,
           COALESCE(d.term, '') AS term,
           COALESCE(d.citizenship, '') AS citizenship,
           COALESCE(d.years_experience, 0) AS years_experience,
           COALESCE(NULLIF(c.industry, 'Unknown'), '') AS industry,
           -- So a row only asks for a logo we actually hold, rather than
           -- firing a request per company and letting most of them 404.
           COALESCE(i.ok, 0) AS has_icon,
           COALESCE(pi.rank, :unranked) AS industry_rank,
           COALESCE(t.status, 'new') AS status,
           COALESCE(t.notes, '') AS notes,
           t.updated_at AS status_changed_at,
           CAST(julianday('now') - julianday(t.updated_at) AS INTEGER) AS days_in_status
    FROM ranked_listings l
    LEFT JOIN companies c ON c.name = l.company
    LEFT JOIN profile_industries pi
           ON pi.industry = NULLIF(c.industry, 'Unknown')
    LEFT JOIN tracker t ON t.listing_id = l.id
    LEFT JOIN listing_details d ON d.listing_id = l.id
    LEFT JOIN company_icons i ON i.company = l.company
"""


DEFAULT_PER_PAGE = 50

# Sort orders the list can be read in. `newest` is the default and is what a
# daily pass wants. `rank` leads with the most preferred industry, which is a
# useful second read but buries everything else for 23 pages. A listing with no
# date sorts last under `newest` rather than first.
SORT_ORDERS = {
    "rank": "industry_rank, l.posted_at DESC, l.id DESC",
    "newest": "(l.posted_at = '') , l.posted_at DESC, l.id DESC",
    "company": "l.company COLLATE NOCASE, l.title COLLATE NOCASE",
}
DEFAULT_SORT = "newest"


def order_by(sort: str) -> str:
    """The ORDER BY clause for a sort name, falling back to the default.

    Looked up in a fixed table, never interpolated from the request, so a
    caller cannot inject SQL through the sort parameter.
    """
    return SORT_ORDERS.get(sort, SORT_ORDERS[DEFAULT_SORT])


def role_clause(roles: list[str], params: dict) -> str:
    """A WHERE fragment matching a listing title against any of `roles`.

    Matching is the same stem comparison the sources use, but SQL cannot call
    it, so this approximates it with a LIKE per meaningful word: a title must
    contain every word of at least one chosen role. That is stricter than the
    source-side matcher and so never widens the list beyond what was fetched.
    """
    from intern_app.sources.role_match import FILLER, normalized_words

    groups = []
    for index, role in enumerate(roles):
        words = [word for word in normalized_words(role) if word not in FILLER]
        if not words:
            continue
        parts = []
        for position, word in enumerate(words):
            key = f"role_{index}_{position}"
            params[key] = f"%{word}%"
            parts.append(f"lower(l.title) LIKE :{key}")
        groups.append("(" + " AND ".join(parts) + ")")
    return "(" + " OR ".join(groups) + ")" if groups else ""


def _new_filters(
    industry: str,
    days: int,
    roles: list[str] | None = None,
    levels: list[str] | None = None,
    educations: list[str] | None = None,
    statuses: list[str] | None = None,
) -> tuple[list[str], dict[str, object]]:
    """The WHERE clauses and parameters shared by the list and its count.

    With no `statuses` the list shows everything except the ignore shelf. A
    tracked listing stays on the board carrying its status, so that scrolling
    past a role you already applied to tells you so.
    """
    # A manual entry is something the user brought in from outside, so it
    # belongs to the tracker and not to the feed of things to discover.
    where = ["l.copy_number = 1", "l.source != 'manual'"]
    params: dict[str, object] = {"unranked": UNRANKED}

    if statuses:
        keys = []
        for index, status in enumerate(statuses):
            key = f"status_{index}"
            params[key] = status
            keys.append(f":{key}")
        where.append(f"COALESCE(t.status, 'new') IN ({', '.join(keys)})")
    else:
        where.append("COALESCE(t.status, 'new') != :ignored")
        params["ignored"] = IGNORED

    if industry:
        where.append("COALESCE(NULLIF(c.industry, 'Unknown'), '') = :industry")
        params["industry"] = industry
    if days:
        where.append("l.posted_at >= date('now', :cutoff)")
        params["cutoff"] = f"-{int(days)} days"
    if roles:
        clause = role_clause(roles, params)
        if clause:
            where.append(clause)
    if levels:
        keys = []
        for index, level in enumerate(levels):
            key = f"level_{index}"
            params[key] = level
            keys.append(f":{key}")
        where.append(f"COALESCE(d.level, '') IN ({', '.join(keys)})")
    if educations:
        keys = []
        for index, education in enumerate(educations):
            key = f"education_{index}"
            params[key] = education
            keys.append(f":{key}")
        where.append(f"COALESCE(d.education, '') IN ({', '.join(keys)})")
    return where, params


def list_new(
    conn: sqlite3.Connection,
    *,
    industry: str = "",
    days: int = 0,
    roles: list[str] | None = None,
    levels: list[str] | None = None,
    educations: list[str] | None = None,
    statuses: list[str] | None = None,
    sort: str = DEFAULT_SORT,
    page: int = 1,
    per_page: int = DEFAULT_PER_PAGE,
) -> list[sqlite3.Row]:
    """One page of the board, best-matching industry first.

    Paging is not a nicety here. Ordering puts the top-ranked industry first,
    and there are over a thousand listings in it, so a single capped page could
    never reach the user's second or third choice at all.

    `days` limits to recently posted when set, which matters because a source
    will happily return a posting from last year.
    """
    where, params = _new_filters(industry, days, roles, levels, educations, statuses)
    params["limit"] = max(1, per_page)
    params["offset"] = max(0, (max(1, page) - 1) * max(1, per_page))

    sql = f"""
        {SELECT_LISTINGS}
        WHERE {" AND ".join(where)}
        ORDER BY {order_by(sort)}
        LIMIT :limit OFFSET :offset
    """
    return conn.execute(sql, params).fetchall()


def count_new(
    conn: sqlite3.Connection,
    *,
    industry: str = "",
    days: int = 0,
    roles: list[str] | None = None,
    levels: list[str] | None = None,
    educations: list[str] | None = None,
    statuses: list[str] | None = None,
) -> int:
    """How many listings match, so the pager knows where it ends."""
    where, params = _new_filters(industry, days, roles, levels, educations, statuses)
    sql = f"""
        {SELECT_LISTINGS}
        WHERE {" AND ".join(where)}
    """
    # Suppression is justified: every clause in `where` is a literal written
    # above, and every user value is bound as a named parameter.
    return conn.execute(f"SELECT COUNT(*) FROM ({sql})", params).fetchone()[0]  # noqa: S608


def new_counts_by_industry(conn: sqlite3.Connection) -> dict[str, int]:
    """Unacted listings per industry, for the rank rail and the backlog line.

    An unclassified industry is counted under "" rather than being dropped.
    """
    sql = f"""
        {SELECT_LISTINGS}
        WHERE COALESCE(t.status, 'new') = 'new' AND l.copy_number = 1
    """
    rows = conn.execute(
        f"SELECT industry, COUNT(*) AS n FROM ({sql}) GROUP BY industry",  # noqa: S608
        {"unranked": UNRANKED},
    ).fetchall()
    return {row["industry"]: row["n"] for row in rows}


def _search_filters(text: str, industry: str, status: str) -> tuple[list[str], dict[str, object]]:
    """The WHERE clauses and parameters shared by the search and its count."""
    where = ["1 = 1"]
    params: dict[str, object] = {"unranked": UNRANKED}

    if text:
        where.append("(l.title LIKE :text OR l.company LIKE :text OR l.location LIKE :text)")
        params["text"] = f"%{text}%"
    if industry:
        where.append("COALESCE(NULLIF(c.industry, 'Unknown'), '') = :industry")
        params["industry"] = industry
    if status:
        where.append("COALESCE(t.status, 'new') = :status")
        params["status"] = status
    return where, params


def search_listings(
    conn: sqlite3.Connection,
    *,
    text: str = "",
    industry: str = "",
    status: str = "",
    sort: str = DEFAULT_SORT,
    page: int = 1,
    per_page: int = DEFAULT_PER_PAGE,
) -> list[sqlite3.Row]:
    """One page of every stored listing, filtered. The Search tab reads this.

    Unlike the dashboard this does not collapse duplicate postings: searching is
    how you reach a specific apply link, so every copy stays visible.
    """
    where, params = _search_filters(text, industry, status)
    params["limit"] = max(1, per_page)
    params["offset"] = max(0, (max(1, page) - 1) * max(1, per_page))

    sql = f"""
        {SELECT_LISTINGS}
        WHERE {" AND ".join(where)}
        ORDER BY {order_by(sort)}
        LIMIT :limit OFFSET :offset
    """
    return conn.execute(sql, params).fetchall()


def count_search(
    conn: sqlite3.Connection, *, text: str = "", industry: str = "", status: str = ""
) -> int:
    """How many listings the search matches in total, not just on this page."""
    where, params = _search_filters(text, industry, status)
    sql = f"""
        {SELECT_LISTINGS}
        WHERE {" AND ".join(where)}
    """
    return conn.execute(f"SELECT COUNT(*) FROM ({sql})", params).fetchone()[0]  # noqa: S608


def list_tracked(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    """Everything I have acted on, grouped by status in pipeline order."""
    sql = f"""
        {SELECT_LISTINGS}
        WHERE t.status IN ({",".join(f"'{name}'" for name in ACTIVE)})
          AND l.copy_number = 1
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


RANGES = (3, 7, 14, 30, 90)
DEFAULT_RANGE = 7


def load_activity(conn: sqlite3.Connection, days: int = DEFAULT_RANGE) -> list[dict]:
    """One entry per day: how many applications went out, and to whom.

    Every day in the window is returned, including the empty ones, because a
    gap in a job search is information and a chart that silently drops it
    reads as a run of steady effort.

    A listing counts on the first day it reached `applied`, so moving it on to
    interviewing later does not move or duplicate the application.

    Days are local days, not UTC ones. History is stored in UTC, and applying
    at nine in the evening is already tomorrow in UTC, so comparing raw dates
    puts the application on a bar the user never lived through.
    """
    window = max(1, days)
    rows = conn.execute(
        """
        WITH first_applied AS (
            SELECT listing_id, MIN(changed_at) AS sent_at
            FROM tracker_history
            WHERE status = 'applied'
            GROUP BY listing_id
        )
        SELECT date(f.sent_at, 'localtime') AS day, l.company, COALESCE(i.ok, 0) AS has_icon
        FROM first_applied f
        JOIN listings l ON l.id = f.listing_id
        LEFT JOIN company_icons i ON i.company = l.company
        WHERE date(f.sent_at, 'localtime') >= date('now', 'localtime', :cutoff)
        ORDER BY f.sent_at
        """,
        {"cutoff": f"-{window - 1} days"},
    ).fetchall()

    by_day: dict[str, list[dict]] = {}
    for row in rows:
        by_day.setdefault(row["day"], []).append(
            {"company": row["company"], "has_icon": bool(row["has_icon"])}
        )

    today = conn.execute("SELECT date('now', 'localtime') AS d").fetchone()["d"]
    days_back = conn.execute(
        "SELECT date(:today, :offset) AS d", {"today": today, "offset": f"-{window - 1} days"}
    ).fetchone()["d"]
    out = []
    cursor = days_back
    while cursor <= today:
        companies = by_day.get(cursor, [])
        out.append({"day": cursor, "count": len(companies), "companies": companies})
        cursor = conn.execute("SELECT date(:d, '+1 day') AS n", {"d": cursor}).fetchone()["n"]
    return out


def board_status_counts(conn: sqlite3.Connection) -> dict[str, int]:
    """How many board rows sit at each status, for the filter chips.

    Built on SELECT_LISTINGS rather than on its own query, because the dedupe
    picks one copy of a repeated posting and the two have to pick the same one.
    A chip reading 9 must mean nine rows appear when it is chosen.
    `status_counts` answers a different question, about the tracker.
    """
    # Suppression is justified: the only interpolation is a module constant.
    sql = f"""
        SELECT status, COUNT(*) AS n
        FROM ({SELECT_LISTINGS} WHERE l.copy_number = 1 AND l.source != 'manual')
        GROUP BY status
    """  # noqa: S608
    rows = conn.execute(sql, {"unranked": UNRANKED}).fetchall()
    return {row["status"]: row["n"] for row in rows}


def ignore_listing(conn: sqlite3.Connection, listing_id: int) -> None:
    """Push a listing onto the ignore shelf, off the board.

    Ignoring is a tracker status rather than a delete, so the reason it left
    is recoverable and the row can come back.
    """
    set_status(conn, listing_id, IGNORED)


def restore_listing(conn: sqlite3.Connection, listing_id: int) -> None:
    """Take a listing back off the ignore shelf."""
    set_status(conn, listing_id, "new")


def level_counts(conn: sqlite3.Connection) -> dict[str, int]:
    """Unacted listings per level, for the intern / new grad filter.

    An unread title counts under "", so the UI can say how many are still
    waiting on `intern-app clean` rather than pretending they are "other".
    """
    sql = f"""
        {SELECT_LISTINGS}
        WHERE COALESCE(t.status, 'new') = 'new' AND l.copy_number = 1
    """
    rows = conn.execute(
        f"SELECT level, COUNT(*) AS n FROM ({sql}) GROUP BY level",  # noqa: S608
        {"unranked": UNRANKED},
    ).fetchall()
    return {row["level"]: row["n"] for row in rows}


def education_counts(conn: sqlite3.Connection) -> dict[str, int]:
    """Unacted listings per degree, for the education filter.

    Same shape as `level_counts`, including the "" bucket for a title that has
    not been read yet. `any` is not a degree requirement — it is what most
    postings say, which is nothing — so the filter shows it as its own choice
    rather than folding it into the others.
    """
    sql = f"""
        {SELECT_LISTINGS}
        WHERE COALESCE(t.status, 'new') = 'new' AND l.copy_number = 1
    """
    rows = conn.execute(
        f"SELECT education, COUNT(*) AS n FROM ({sql}) GROUP BY education",  # noqa: S608
        {"unranked": UNRANKED},
    ).fetchall()
    return {row["education"]: row["n"] for row in rows}


def known_industries(conn: sqlite3.Connection) -> list[str]:
    """Industries actually present in the stored listings, for the filter."""
    rows = conn.execute(
        """
        SELECT DISTINCT c.industry FROM listings l
        JOIN companies c ON c.name = l.company
        WHERE c.industry IS NOT NULL AND c.industry NOT IN ('', 'Unknown')
        ORDER BY c.industry
        """
    ).fetchall()
    return [row["industry"] for row in rows]


def add_manual_listing(
    conn: sqlite3.Connection,
    *,
    title: str,
    company: str,
    location: str = "",
    url: str = "",
    posted_at: str = "",
    status: str = "applied",
    notes: str = "",
) -> int:
    """Store a job I found outside the app and put it straight in the tracker.

    Most of what I apply to arrives through a source, but not all of it — a
    referral, a careers page I was sent, a recruiter email. Those have to live
    in the tracker too or the tracker is not the whole picture.

    `url` is what listings dedupe on and it is optional here, so a listing with
    no link gets a stable local one rather than colliding with every other
    blank. The listing is stored with `source = 'manual'` so it is always clear
    which rows I typed myself.
    """
    from intern_app.sources.base import normalize

    title = title.strip()
    company = company.strip()
    if not title or not company:
        raise ValueError("a manual listing needs both a title and a company")
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}, got {status!r}")

    link = url.strip()
    if not link:
        slug = f"{company} {title}".lower().replace(" ", "-")
        link = f"manual:{slug}"

    db.upsert_listings(
        conn,
        [
            normalize(
                title=title,
                company=company,
                location=location.strip(),
                url=link,
                description="",
                posted_at=posted_at.strip(),
                source="manual",
                full_text=False,
            )
        ],
    )
    listing_id = conn.execute("SELECT id FROM listings WHERE url = ?", (link,)).fetchone()["id"]
    set_status(conn, listing_id, status)
    if notes.strip():
        conn.execute(
            "UPDATE tracker SET notes = ? WHERE listing_id = ?", (notes.strip(), listing_id)
        )
    return int(listing_id)
