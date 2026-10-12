"""Fetching one posting's full description from the ATS that hosts it.

CLAUDE.md allows documented APIs and public board endpoints, and nothing else.
Greenhouse, Lever and Ashby each publish one, and between them they host 900 of
the stored listings:

    greenhouse  https://boards-api.greenhouse.io/v1/boards/<slug>/jobs/<id>
    lever       https://api.lever.co/v0/postings/<slug>/<id>?mode=json
    ashby       https://api.ashbyhq.com/posting-api/job-board/<slug>

Workday, iCIMS, Taleo and company career pages have no published API, so a
description there could only be had by fetching and parsing the page. That is
scraping, and this module does not do it.

Ashby serves a whole board in one call rather than one posting at a time, so
its descriptions are read per board and matched back by posting id.
"""

from __future__ import annotations

import re
import sqlite3
from html import unescape
from urllib.parse import urlsplit

import httpx

from intern_app import db

SOURCE = "ats_detail"

GREENHOUSE_JOB = re.compile(
    r"(?:boards|job-boards)(?:\.eu)?\.greenhouse\.io/(?:embed/job_app\?for=)?([^/?#]+)/jobs/(\d+)"
)
LEVER_JOB = re.compile(r"jobs\.(eu\.)?lever\.co/([^/?#]+)/([0-9a-f-]{36})")
ASHBY_JOB = re.compile(r"jobs\.ashbyhq\.com/([^/?#]+)/([0-9a-f-]{36})")

TAGS = re.compile(r"<[^>]+>")
BLANKS = re.compile(r"\n{3,}")


def strip_html(text: str) -> str:
    """Readable plain text from an HTML description.

    Greenhouse returns its content HTML-escaped inside JSON, so it is unescaped
    twice: once to get the tags back, once for the entities inside them.
    """
    unescaped = unescape(unescape(text))
    broken = re.sub(r"<(br|/p|/div|/li|/h\d)[^>]*>", "\n", unescaped, flags=re.IGNORECASE)
    return BLANKS.sub("\n\n", TAGS.sub("", broken)).strip()


def api_url(url: str) -> tuple[str, str, str] | None:
    """The (board, api url, posting id) for an apply link, or None.

    Returns the board so the caller knows whether the reply is one posting or a
    whole board, and the posting id so an Ashby board can be matched back.
    """
    found = GREENHOUSE_JOB.search(url)
    if found:
        slug, job_id = found.groups()
        return (
            "greenhouse",
            f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs/{job_id}",
            job_id,
        )

    found = LEVER_JOB.search(url)
    if found:
        eu, slug, job_id = found.groups()
        host = "api.eu.lever.co" if eu else "api.lever.co"
        return "lever", f"https://{host}/v0/postings/{slug}/{job_id}?mode=json", job_id

    found = ASHBY_JOB.search(url)
    if found:
        slug, job_id = found.groups()
        return "ashby", f"https://api.ashbyhq.com/posting-api/job-board/{slug}", job_id

    return None


def description_from(board: str, payload: dict, job_id: str) -> str:
    """The posting's text, however the board shapes its reply."""
    if board == "greenhouse":
        return strip_html(payload.get("content", ""))
    if board == "lever":
        return (
            payload.get("descriptionPlain") or strip_html(payload.get("description", ""))
        ).strip()
    for job in payload.get("jobs", []):
        if str(job.get("id", "")) == job_id:
            return (
                job.get("descriptionPlain") or strip_html(job.get("descriptionHtml", ""))
            ).strip()
    return ""


def listings_needing_description(conn: sqlite3.Connection, limit: int = 0) -> list[sqlite3.Row]:
    """Listings on one of the three boards that have no full text yet."""
    sql = """
        SELECT id, url FROM listings
        WHERE full_text = 0
          AND (url LIKE '%greenhouse.io%' OR url LIKE '%lever.co%' OR url LIKE '%ashbyhq.com%')
        ORDER BY first_seen DESC, id DESC
    """
    if limit:
        return conn.execute(sql + " LIMIT ?", (limit,)).fetchall()
    return conn.execute(sql).fetchall()


def store_description(conn: sqlite3.Connection, listing_id: int, text: str) -> None:
    """Attach a full description to a listing and mark it as complete.

    `full_text` is the gate CLAUDE.md puts on skill extraction, so it is only
    set when the whole posting really is stored.
    """
    conn.execute(
        "UPDATE listings SET description = ?, full_text = 1 WHERE id = ?",
        (text, listing_id),
    )


def collect_descriptions(conn: sqlite3.Connection, *, limit: int = 0) -> dict[str, int]:
    """Fetch the full text of every listing on a board that publishes one.

    An Ashby board arrives whole, so its reply is kept and reused for every
    other listing on the same board instead of being requested again.
    """
    found = {"tried": 0, "stored": 0, "empty": 0, "failed": 0}
    boards: dict[str, dict] = {}

    with httpx.Client(timeout=20, follow_redirects=True) as client:
        for row in listings_needing_description(conn, limit):
            target = api_url(row["url"])
            if target is None:
                continue
            board, url, job_id = target
            found["tried"] += 1

            payload = boards.get(url)
            if payload is None:
                try:
                    response = client.get(url)
                except httpx.HTTPError as exc:
                    db.record_api_call(
                        conn, source=SOURCE, endpoint=url, ok=False, error=type(exc).__name__
                    )
                    found["failed"] += 1
                    continue
                db.record_api_call(
                    conn,
                    source=SOURCE,
                    endpoint=url,
                    status_code=response.status_code,
                    ok=response.status_code == 200,
                )
                if response.status_code != 200:
                    found["failed"] += 1
                    continue
                payload = response.json()
                # Only a whole-board reply is worth keeping; a single posting
                # is never asked for twice.
                if board == "ashby":
                    boards[url] = payload

            text = description_from(board, payload, job_id)
            if text:
                store_description(conn, row["id"], text)
                found["stored"] += 1
            else:
                found["empty"] += 1
    return found


def host_of(url: str) -> str:
    """The hostname of an apply link, for reporting what is out of reach."""
    return urlsplit(url).hostname or ""
