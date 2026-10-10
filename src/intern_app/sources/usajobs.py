"""USAJobs: federal internships and new-grad roles.

Three things about this API shape the code:

The whole relevant pool is small. Every federal posting on the student and
graduates hiring paths is 159 rows today, and the API returns up to 500 per
page, so one request fetches all of it. That is better than querying per role:
keyword search here is loose — "software engineer intern" returned a Smithsonian
*Computer Engineer* — so the titles are matched locally instead.

Descriptions are complete but split across fields: `JobSummary` and
`MajorDuties` under `UserArea.Details`, plus a top-level `QualificationSummary`.
`MajorDuties` is a list, not a string. Joined together they run to a median of
5,900 characters, so this is a `full_text=True` source.

The `User-Agent` header must be the email address registered with USAJobs, which
is a requirement of theirs rather than a convention.
"""

from __future__ import annotations

import sqlite3
from typing import Any

import httpx

from intern_app import db
from intern_app.config import settings
from intern_app.sources import quota
from intern_app.sources.base import Listing, normalize
from intern_app.sources.role_match import title_matches_role

SOURCE = "usajobs"
ENDPOINT = "https://data.usajobs.gov/api/search"

# The two hiring paths that mean "student or recent graduate" here.
HIRING_PATHS = "student;graduates"

# The API's maximum, which is more than the whole pool.
PER_PAGE = 500


def request_headers() -> dict[str, str]:
    """Headers USAJobs requires.

    `User-Agent` has to be the registered email address; a request without it is
    rejected. The key goes in `Authorization-Key` and is never logged.
    """
    cfg = settings()
    return {
        "Host": "data.usajobs.gov",
        "User-Agent": cfg.require("USAJOBS_EMAIL"),
        "Authorization-Key": cfg.require("USAJOBS_API_KEY"),
    }


def as_text(value: Any) -> str:
    """Flatten a field that may arrive as a string or a list of strings."""
    if isinstance(value, list):
        return " ".join(str(part) for part in value if part)
    return str(value or "")


def description_of(descriptor: dict) -> str:
    """The full posting, assembled from the fields it is split across."""
    details = descriptor.get("UserArea", {}).get("Details", {})
    parts = (
        as_text(details.get("JobSummary")),
        as_text(details.get("MajorDuties")),
        as_text(descriptor.get("QualificationSummary")),
    )
    return "\n\n".join(part.strip() for part in parts if part.strip())


def to_listing(descriptor: dict) -> Listing:
    """One USAJobs posting as a normalized listing."""
    places = [place.get("LocationName", "") for place in descriptor.get("PositionLocation") or []]
    return normalize(
        title=descriptor.get("PositionTitle"),
        company=descriptor.get("OrganizationName"),
        location=", ".join(name for name in places if name),
        url=descriptor.get("PositionURI"),
        description=description_of(descriptor),
        posted_at=(descriptor.get("PublicationStartDate") or "")[:10],
        source=SOURCE,
        full_text=True,
        is_html=True,
    )


def fetch_usajobs(conn: sqlite3.Connection, roles: list[str]) -> list[Listing]:
    """Federal student and new-grad postings matching any of my roles.

    Fetches the whole pool and filters locally, which takes one request. A
    posting with no usable description is skipped rather than stored as full
    text with nothing in it.
    """
    quota.check(conn, SOURCE)
    headers = request_headers()
    found: dict[str, Listing] = {}

    with httpx.Client(timeout=60, headers=headers) as http:
        page = 1
        while True:
            if not quota.may_call(conn, SOURCE, check_interval=False):
                break

            items, total = _get_page(conn, http, page)
            for item in items:
                descriptor = item.get("MatchedObjectDescriptor") or {}
                title = descriptor.get("PositionTitle") or ""
                if not any(title_matches_role(title, role) for role in roles):
                    continue
                if not description_of(descriptor).strip():
                    continue
                listing = to_listing(descriptor)
                found.setdefault(listing["url"], listing)

            if not items or page * PER_PAGE >= total:
                break
            page += 1

    return list(found.values())


def _get_page(conn: sqlite3.Connection, http: httpx.Client, page: int) -> tuple[list[dict], int]:
    """One request, recorded either way. Returns its items and the pool size."""
    params = {"HiringPath": HIRING_PATHS, "ResultsPerPage": PER_PAGE, "Page": page}
    try:
        response = http.get(ENDPOINT, params=params)
    except httpx.HTTPError as exc:
        db.record_api_call(
            conn, source=SOURCE, endpoint=ENDPOINT, ok=False, error=type(exc).__name__
        )
        return [], 0

    db.record_api_call(
        conn,
        source=SOURCE,
        endpoint=ENDPOINT,
        status_code=response.status_code,
        ok=response.is_success,
    )
    if not response.is_success:
        return [], 0

    try:
        result = response.json().get("SearchResult") or {}
    except ValueError as exc:
        db.record_api_call(
            conn,
            source=SOURCE,
            endpoint=ENDPOINT,
            ok=False,
            error=f"bad JSON: {type(exc).__name__}",
        )
        return [], 0

    return result.get("SearchResultItems") or [], int(result.get("SearchResultCountAll") or 0)
