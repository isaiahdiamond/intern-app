"""Reading a job posting's own text, rather than guessing from its title.

A title says what the board chose to put in it. Half of them state no degree
and a third state no level, so reading titles alone left 93% of listings marked
"no degree stated" and 688 marked "other" on evidence that was never there.

The posting body does say these things, so where the full text has been
collected this replaces the title-only reading. The raw title still stays
untouched in `listings`.

This runs on a smaller model than the rest of the app. It is a long-input,
short-output job where the volume of text is the cost and the task itself is
plain reading, so Haiku does it for about a fortieth of what Opus would.
"""

from __future__ import annotations

import sqlite3

from pydantic import BaseModel

from intern_app import db
from intern_app.llm.client import call_structured, load_prompt

LEVELS = ("intern", "coop", "new_grad", "other")
EDUCATION = ("undergrad", "masters", "phd", "any")
CITIZENSHIP = ("us_citizen", "clearance", "no_sponsorship", "")

MODEL = "claude-haiku-5-5"
MAX_TOKENS = 1000

# A posting is sent one at a time rather than batched: they run to ten thousand
# characters each, so a batch would blow the context and one bad reply would
# lose the whole group.
MAX_DESCRIPTION = 14000


class PostingReading(BaseModel):
    clean_title: str
    level: str
    education: str
    term: str = ""
    years_experience: int = 0
    citizenship: str = ""


def one_of(value: str, allowed: tuple[str, ...], fallback: str) -> str:
    """A reply's value when it is in the allowed set, otherwise the fallback.

    The dashboard filters on these, so an unknown value would quietly hide a
    listing rather than show it wrongly.
    """
    cleaned = value.strip().lower()
    return cleaned if cleaned in allowed else fallback


def read_posting(conn: sqlite3.Connection, row: sqlite3.Row) -> bool:
    """Read one posting and store what it says. True when something was stored."""
    prompt = load_prompt(
        "read_posting",
        title=row["title"],
        description=(row["description"] or "")[:MAX_DESCRIPTION],
    )

    result = call_structured(
        conn,
        prompt_name="read_posting",
        prompt=prompt,
        output_model=PostingReading,
        listing_id=row["id"],
        max_tokens=MAX_TOKENS,
        model=MODEL,
    )

    db.set_listing_detail(
        conn,
        listing_id=row["id"],
        clean_title=result.clean_title.strip() or row["title"],
        level=one_of(result.level, LEVELS, "other"),
        education=one_of(result.education, EDUCATION, "any"),
        term=result.term.strip(),
        years_experience=max(0, result.years_experience),
        citizenship=one_of(result.citizenship, CITIZENSHIP, ""),
    )
    return True


def listings_with_unread_descriptions(
    conn: sqlite3.Connection, limit: int = 0
) -> list[sqlite3.Row]:
    """Listings whose full text is stored but has never been read.

    The title-only reading in `listing_details` does not count: this pass is
    what replaces it, so a listing is pending until `read_posting` has run
    against it specifically.
    """
    sql = """
        SELECT l.id, l.title, l.description
        FROM listings l
        WHERE l.full_text = 1
          AND length(l.description) > 200
          AND NOT EXISTS (
              SELECT 1 FROM llm_calls c
              WHERE c.listing_id = l.id AND c.ok = 1 AND c.prompt_name = 'read_posting'
          )
        ORDER BY l.first_seen DESC, l.id DESC
    """
    if limit:
        return conn.execute(sql + " LIMIT ?", (limit,)).fetchall()
    return conn.execute(sql).fetchall()
