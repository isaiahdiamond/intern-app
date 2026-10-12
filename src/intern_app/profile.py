"""Reading and writing the single local profile.

One user for now, so `profile` holds at most one row. Saving is a replace: the
whole answer set is written together, because the onboarding form submits it
together and a half-updated profile is worse than none.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from intern_app.db import utcnow

ROLE_SOURCES = ("chip", "llm_suggested")

# The levels a search can be for. These are the same keys `listing_details`
# stores, so what the profile wants and what a listing is are directly
# comparable. `other` is not here: nobody is looking for an experienced hire.
SEEKING = ("intern", "coop", "new_grad")

# Degrees, lowest first. A listing asking for more than the user has is not one
# they can apply to, so the order is what makes the comparison possible.
DEGREES = ("any", "undergrad", "masters", "phd")


def degree_rank(degree: str) -> int:
    """How far up the ladder a degree is. An unknown one counts as none."""
    name = degree.strip().lower()
    return DEGREES.index(name) if name in DEGREES else 0


def degrees_open_to(degree: str) -> list[str]:
    """The degree requirements someone holding `degree` can actually apply to.

    A master's student can take a posting that asks for a bachelor's, or one
    that asks for nothing. They cannot take one restricted to PhDs. With no
    degree set, nothing is ruled out — the filter is off rather than empty.
    """
    if not degree.strip():
        return []
    ceiling = degree_rank(degree)
    return [name for name in DEGREES if DEGREES.index(name) <= ceiling]


def dedupe(names: list[str]) -> list[str]:
    """Drop repeats and blanks, keeping first-seen order.

    Order matters for industries, where position becomes rank, and the columns
    are UNIQUE, so a repeated value would otherwise be a constraint error.
    """
    kept: list[str] = []
    for name in names:
        cleaned = name.strip()
        if cleaned and cleaned not in kept:
            kept.append(cleaned)
    return kept


def dedupe_pairs(pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Same, for (role, source) pairs, keyed on the role."""
    kept: list[tuple[str, str]] = []
    seen: set[str] = set()
    for role, source in pairs:
        cleaned = role.strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            kept.append((cleaned, source))
    return kept


def save_profile(
    conn: sqlite3.Connection,
    *,
    school: str,
    major: str,
    roles: list[tuple[str, str]],
    industries: list[str],
    education: str = "",
    seeking: list[str] | None = None,
) -> None:
    """Write the profile, its roles, its ranked industries and what it wants.

    `roles` is a list of (role, source) pairs. `industries` is in preference
    order — position becomes `rank`, starting at 1, which is what the dashboard
    sorts on.

    Re-running replaces the previous answers rather than adding a second
    profile, which is what makes onboarding editable later.
    """
    for _, source in roles:
        if source not in ROLE_SOURCES:
            raise ValueError(f"role source must be one of {ROLE_SOURCES}, got {source!r}")

    roles = dedupe_pairs(roles)
    industries = dedupe(industries)
    wanted = [name for name in dedupe(seeking or []) if name in SEEKING]
    if education.strip() and education.strip().lower() not in DEGREES:
        raise ValueError(f"education must be one of {DEGREES}, got {education!r}")

    now = utcnow()
    # An explicit transaction, because `with conn:` does nothing on a connection
    # opened with isolation_level=None. Without this, a failure after the DELETE
    # would leave the profile with no roles at all.
    conn.execute("BEGIN")
    try:
        existing = conn.execute("SELECT created_at FROM profile WHERE id = 1").fetchone()
        created_at = existing["created_at"] if existing else now
        conn.execute(
            """
            INSERT INTO profile (id, school, major, education, created_at, updated_at)
            VALUES (1, ?, ?, ?, ?, ?)
            ON CONFLICT (id) DO UPDATE SET
                school = excluded.school,
                major = excluded.major,
                education = excluded.education,
                updated_at = excluded.updated_at
            """,
            (school.strip(), major.strip(), education.strip().lower(), created_at, now),
        )

        conn.execute("DELETE FROM profile_roles")
        conn.executemany(
            "INSERT INTO profile_roles (role, source) VALUES (?, ?)",
            [(role.strip(), source) for role, source in roles if role.strip()],
        )

        conn.execute("DELETE FROM profile_levels")
        conn.executemany(
            "INSERT INTO profile_levels (level) VALUES (?)", [(name,) for name in wanted]
        )

        conn.execute("DELETE FROM profile_industries")
        conn.executemany(
            "INSERT INTO profile_industries (industry, rank) VALUES (?, ?)",
            [(name.strip(), i) for i, name in enumerate(industries, start=1) if name.strip()],
        )
    except Exception:
        conn.execute("ROLLBACK")
        raise
    conn.execute("COMMIT")


def load_profile(conn: sqlite3.Connection) -> dict[str, Any] | None:
    """The whole profile, or None when onboarding has not been completed."""
    row = conn.execute("SELECT * FROM profile WHERE id = 1").fetchone()
    if row is None:
        return None
    return {
        "school": row["school"],
        "major": row["major"],
        "education": row["education"],
        "seeking": load_seeking(conn),
        "roles": load_role_names(conn),
        "industries": load_industry_ranking(conn),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def load_role_names(conn: sqlite3.Connection) -> list[str]:
    """Just the role strings, which is what the sources are queried with."""
    rows = conn.execute("SELECT role FROM profile_roles ORDER BY id").fetchall()
    return [row["role"] for row in rows]


def load_seeking(conn: sqlite3.Connection) -> list[str]:
    """The levels the search is for, in the order the app lists them."""
    stored = {row["level"] for row in conn.execute("SELECT level FROM profile_levels")}
    return [name for name in SEEKING if name in stored]


def load_industry_ranking(conn: sqlite3.Connection) -> list[str]:
    """Industries in preference order, most preferred first."""
    rows = conn.execute("SELECT industry FROM profile_industries ORDER BY rank").fetchall()
    return [row["industry"] for row in rows]


def is_onboarded(conn: sqlite3.Connection) -> bool:
    """True once a profile exists with at least one role.

    A profile with no roles cannot drive a fetch, so it does not count as done.
    """
    row = conn.execute(
        "SELECT (SELECT COUNT(*) FROM profile_roles) AS roles,"
        "       (SELECT COUNT(*) FROM profile WHERE id = 1) AS profiles"
    ).fetchone()
    return bool(row["profiles"]) and bool(row["roles"])
