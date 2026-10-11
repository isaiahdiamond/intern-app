"""Reading a job title: the role, the level, the degree, the term.

Board titles run everything together — "Machine Learning Scientist Intern -
TikTok-Recommendation - 2027 Start - PhD". Nearly half carry a dash separator,
a fifth carry a year, and a third never state their level at all, so this is
judgement rather than a regular expression.

The raw title is never overwritten. The reading lands in `listing_details`, so
a bad one can be recomputed without losing what the source actually said.
"""

from __future__ import annotations

import sqlite3

from pydantic import BaseModel

from intern_app import db
from intern_app.llm.client import call_structured, load_prompt

LEVELS = ("intern", "coop", "new_grad", "other")
EDUCATION = ("undergrad", "masters", "phd", "any")

# Forty titles at four fields each overran the default 2,048-token ceiling and
# the reply came back as truncated JSON, losing a batch that had already been
# paid for. Thirty per call with a raised ceiling leaves real headroom.
BATCH_SIZE = 30
MAX_TOKENS = 8000


class TitleReading(BaseModel):
    id: int
    clean_title: str
    level: str
    education: str
    term: str = ""


class TitleReadings(BaseModel):
    titles: list[TitleReading]


def clean_titles(conn: sqlite3.Connection, rows: list[sqlite3.Row]) -> int:
    """Read each listing's title and store the result. Returns how many landed.

    A reply that names a level or education outside the known set is corrected
    to the safest value rather than stored, because the dashboard filters on
    these and an unknown value would simply hide the listing.
    """
    stored = 0

    for start in range(0, len(rows), BATCH_SIZE):
        batch = rows[start : start + BATCH_SIZE]
        listed = "\n".join(f"{row['id']}: {row['title']}" for row in batch)
        prompt = load_prompt("clean_title", titles=listed)

        result = call_structured(
            conn,
            prompt_name="clean_title",
            prompt=prompt,
            output_model=TitleReadings,
            max_tokens=MAX_TOKENS,
        )

        originals = {row["id"]: row["title"] for row in batch}
        for reading in result.titles:
            if reading.id not in originals:
                continue
            db.set_listing_detail(
                conn,
                listing_id=reading.id,
                clean_title=reading.clean_title.strip() or originals[reading.id],
                level=reading.level.strip().lower()
                if reading.level.strip().lower() in LEVELS
                else "other",
                education=reading.education.strip().lower()
                if reading.education.strip().lower() in EDUCATION
                else "any",
                term=reading.term.strip(),
            )
            stored += 1

    return stored
