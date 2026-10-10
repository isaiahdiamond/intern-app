"""The Muse. One function, queried per role, returning normalized listings.

Two things about this API shape the code around:

The Muse has no keyword search. A `q` parameter is silently ignored and returns
the whole corpus, so a role title cannot be sent as a query. The only filters
are `category`, `level`, and `location`, and a category outside its fixed list
returns zero results with no error. So each role maps to Muse categories, and
the role is matched against the returned titles here instead.

`categories` is a job function ("Software Engineering"), not an industry, so no
industry tag can come from this source. That is left to classification.

Levels queried are Internship and Entry Level, which is what covers internships
and new-grad roles.
"""

from __future__ import annotations

import sqlite3

import httpx

from intern_app import db
from intern_app.config import settings
from intern_app.sources import quota
from intern_app.sources.base import Listing, normalize
from intern_app.sources.role_match import normalized_words, phrase_in, title_matches_role

SOURCE = "muse"
ENDPOINT = "https://www.themuse.com/api/public/jobs"

# Levels that mean "internship or new grad" in Muse's vocabulary.
LEVELS = ("Internship", "Entry Level")

# Muse's real category names, confirmed against the live API. A name outside
# this list returns zero rows silently, so guessing here costs listings.
CATEGORIES_BY_ROLE: dict[str, tuple[str, ...]] = {
    "software engineer": ("Software Engineering",),
    "backend engineer": ("Software Engineering",),
    "frontend engineer": ("Software Engineering",),
    "full stack engineer": ("Software Engineering",),
    "software developer": ("Software Engineering",),
    "mobile engineer": ("Software Engineering",),
    "site reliability engineer": ("Software Engineering", "Computer and IT"),
    "qa engineer": ("Software Engineering",),
    "security engineer": ("Software Engineering", "Computer and IT"),
    "embedded software": ("Software Engineering", "Science and Engineering"),
    "firmware engineer": ("Software Engineering", "Science and Engineering"),
    "machine learning": ("Software Engineering", "Data and Analytics"),
    "data science": ("Data and Analytics",),
    "data scientist": ("Data and Analytics",),
    "data analyst": ("Data and Analytics",),
    "data engineer": ("Data and Analytics", "Software Engineering"),
    "business intelligence": ("Data and Analytics",),
    "statistician": ("Data and Analytics",),
    "quantitative research": ("Data and Analytics", "Accounting and Finance"),
    "quantitative trading": ("Accounting and Finance", "Data and Analytics"),
    "quantitative developer": ("Accounting and Finance", "Software Engineering"),
    "actuarial": ("Accounting and Finance",),
    "research": ("Science and Engineering",),
    "hardware engineer": ("Science and Engineering",),
    "fpga engineer": ("Science and Engineering",),
    "signal processing": ("Science and Engineering",),
    "business analyst": ("Business Operations",),
    "it": ("Computer and IT",),
    "database administrator": ("Computer and IT",),
    "security analyst": ("Computer and IT",),
    "product": ("Product Management",),
}


def categories_for_role(role: str) -> tuple[str, ...]:
    """Which Muse categories to search for a role.

    Keys are matched as whole words, never as substrings: a substring match sent
    every role containing the letters "it" to Computer and IT, and "product"
    matched "Production Engineer". The longest matching key wins, so
    "quantitative research" beats "research" for a quant role.
    """
    words = normalized_words(role)
    matches = [key for key in CATEGORIES_BY_ROLE if phrase_in(key, words)]
    if not matches:
        return ()
    return CATEGORIES_BY_ROLE[max(matches, key=len)]


def to_listing(job: dict) -> Listing:
    """One Muse job as a normalized listing.

    `contents` is the full posting as HTML, so `full_text` is True and the
    description goes through the HTML cleaner.
    """
    locations = [place.get("name", "") for place in job.get("locations") or []]
    company = (job.get("company") or {}).get("name", "")
    return normalize(
        title=job.get("name"),
        company=company,
        location=", ".join(name for name in locations if name),
        url=(job.get("refs") or {}).get("landing_page"),
        description=job.get("contents") or "",
        posted_at=job.get("publication_date"),
        source=SOURCE,
        full_text=True,
        is_html=True,
    )


class RateLimitedError(RuntimeError):
    """The API asked us to slow down, so the run stops rather than hammering it."""


def fetch_muse(
    conn: sqlite3.Connection,
    roles: list[str],
    *,
    locations: list[str] | None = None,
    max_pages: int = 8,
) -> list[Listing]:
    """Listings from The Muse for the given roles, internship and new-grad level.

    Each (category, level, location) is requested **once**, not once per role,
    and every returned job is then tested against every role. Fetching per role
    re-requested the same Software Engineering pages for each of eight roles,
    which burnt the daily budget on duplicates and still read only the first
    couple of pages.

    `max_pages` bounds each query at 20 jobs a page. A cap is unavoidable:
    Software Engineering alone has 874 internships and 30,352 entry-level
    postings, so reading every page is neither affordable nor useful. The
    default order is roughly newest-first — `descending=true` returns the
    oldest, despite the name — so the cap keeps the freshest postings.
    """
    api_key = settings().require("MUSE_API_KEY")
    quota.check(conn, SOURCE)

    wanted = [role for role in roles if categories_for_role(role)]
    found: dict[str, Listing] = {}

    with httpx.Client(timeout=30) as http:
        for category, level, location in _queries_for(wanted, locations):
            for page in range(max_pages):
                if not quota.may_call(conn, SOURCE, check_interval=False):
                    return list(found.values())

                params: dict[str, object] = {
                    "page": page,
                    "category": category,
                    "level": level,
                    "api_key": api_key,
                }
                if location:
                    params["location"] = location

                try:
                    jobs, pages = _get_page(conn, http, params)
                except RateLimitedError:
                    return list(found.values())

                for job in jobs:
                    title = job.get("name") or ""
                    if not any(title_matches_role(title, role) for role in wanted):
                        continue
                    listing = to_listing(job)
                    found.setdefault(listing["url"], listing)

                if page + 1 >= pages:
                    break

    return list(found.values())


def _queries_for(roles: list[str], locations: list[str] | None) -> list[tuple[str, str, str]]:
    """Every (category, level, location) to request, each exactly once.

    Several roles share a category, and the category is what the API filters on,
    so the request does not need to know which role asked for it.
    """
    places = locations or [""]
    categories: list[str] = []
    for role in roles:
        for category in categories_for_role(role):
            if category not in categories:
                categories.append(category)

    return [
        (category, level, location)
        for category in categories
        for level in LEVELS
        for location in places
    ]


def _get_page(conn: sqlite3.Connection, http: httpx.Client, params: dict) -> tuple[list[dict], int]:
    """One request, recorded either way. Returns its jobs and the page count.

    The endpoint is recorded without its query string, since the API key rides
    in there. A failed call still spends quota, so it is still recorded. A 429
    raises `RateLimitedError` so the caller stops instead of continuing to call.
    """
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
    if response.status_code == 429:
        raise RateLimitedError("The Muse returned 429; stopping this run.")
    if not response.is_success:
        return [], 0

    try:
        payload = response.json()
    except ValueError as exc:
        db.record_api_call(
            conn,
            source=SOURCE,
            endpoint=ENDPOINT,
            ok=False,
            error=f"bad JSON: {type(exc).__name__}",
        )
        return [], 0

    return payload.get("results") or [], int(payload.get("page_count") or 0)
