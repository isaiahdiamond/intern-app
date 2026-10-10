"""Adzuna: discovery only, because its descriptions are truncated.

Three things shape this source:

Descriptions come back cut off at 500 characters with an ellipsis, so every
listing is `full_text=False` and the description is dropped rather than stored
half-finished. Adzuna is here for coverage, not for text.

**The redirect URL embeds the API key.** Adzuna returns
`...?utm_medium=api&utm_source=<app_id>`, and the app id is a credential. It is
stripped before anything is stored, or every listing row would carry the key and
so would any export.

Their terms require the "Jobs by Adzuna" attribution wherever these appear,
which the UI carries via the source name.
"""

from __future__ import annotations

import sqlite3
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx

from intern_app import db
from intern_app.config import settings
from intern_app.sources import quota
from intern_app.sources.base import Listing, normalize
from intern_app.sources.role_match import title_matches_role
from intern_app.sources.us_filter import is_us_or_remote

SOURCE = "adzuna"
ENDPOINT = "https://api.adzuna.com/v1/api/jobs/us/search/1"

ATTRIBUTION = "Jobs by Adzuna"

# 50 is their maximum per page. One page per role keeps a run inside the free
# tier's monthly allowance, which the quota table also enforces.
PER_PAGE = 50


def clean_url(url: str, *, secrets: tuple[str, ...] = ()) -> str:
    """Drop the API key from an Adzuna redirect URL, or refuse the URL.

    `utm_source` is literally the app id, so it is removed — case-insensitively,
    because the key name is not guaranteed to arrive lowercase — and the
    fragment is dropped, since a credential there would survive query cleaning.

    Then the real invariant is enforced: if a secret still appears anywhere in
    the result, the URL is rejected outright by returning "". Stripping one
    known parameter is a guess about where the key sits; checking the finished
    string is a guarantee. `fetch_adzuna` skips listings with no URL, so a
    rejected one is simply not stored.
    """
    if not url:
        return ""

    parts = urlsplit(url)
    kept = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.strip().lower() != "utm_source"
    ]
    cleaned = urlunsplit(parts._replace(query=urlencode(kept), fragment=""))

    for secret in secrets:
        if secret and secret.lower() in cleaned.lower():
            return ""
    return cleaned


def credentials_to_scrub() -> tuple[str, ...]:
    """The values that must never appear in a stored Adzuna URL."""
    cfg = settings()
    return tuple(value for value in (cfg.get("ADZUNA_APP_ID"), cfg.get("ADZUNA_APP_KEY")) if value)


def to_listing(job: dict, *, secrets: tuple[str, ...] | None = None) -> Listing:
    """One Adzuna result as a normalized listing, with no description.

    The description is deliberately empty: theirs is truncated, and a partial
    posting must never reach requirement extraction.
    """
    if secrets is None:
        secrets = credentials_to_scrub()
    return normalize(
        title=job.get("title"),
        company=(job.get("company") or {}).get("display_name"),
        location=(job.get("location") or {}).get("display_name"),
        url=clean_url(job.get("redirect_url") or "", secrets=secrets),
        description="",
        posted_at=(job.get("created") or "")[:10],
        source=SOURCE,
        full_text=False,
    )


def fetch_adzuna(conn: sqlite3.Connection, roles: list[str]) -> list[Listing]:
    """Listings from Adzuna for each role, US only, deduped on url.

    One request per role. Titles are still matched locally, because a keyword
    search returns plenty that only loosely relates to the phrase.
    """
    cfg = settings()
    credentials = {
        "app_id": cfg.require("ADZUNA_APP_ID"),
        "app_key": cfg.require("ADZUNA_APP_KEY"),
    }
    quota.check(conn, SOURCE, needed=len(roles))

    secrets = credentials_to_scrub()
    found: dict[str, Listing] = {}
    with httpx.Client(timeout=45) as http:
        for role in roles:
            if not quota.may_call(conn, SOURCE, check_interval=False):
                break

            for job in _search(conn, http, credentials, role):
                title = job.get("title") or ""
                if not title_matches_role(title, role):
                    continue
                listing = to_listing(job, secrets=secrets)
                if not listing["url"] or not is_us_or_remote(listing["location"]):
                    continue
                found.setdefault(listing["url"], listing)

    return list(found.values())


def _search(
    conn: sqlite3.Connection, http: httpx.Client, credentials: dict, role: str
) -> list[dict]:
    """One keyword search, recorded either way."""
    params = {
        **credentials,
        "what": role,
        "results_per_page": PER_PAGE,
        "content-type": "application/json",
    }
    try:
        response = http.get(ENDPOINT, params=params)
    except httpx.HTTPError as exc:
        db.record_api_call(
            conn, source=SOURCE, endpoint=ENDPOINT, ok=False, error=type(exc).__name__
        )
        return []

    db.record_api_call(
        conn,
        source=SOURCE,
        endpoint=ENDPOINT,
        status_code=response.status_code,
        ok=response.is_success,
    )
    if not response.is_success:
        return []

    try:
        return response.json().get("results") or []
    except ValueError as exc:
        db.record_api_call(
            conn,
            source=SOURCE,
            endpoint=ENDPOINT,
            ok=False,
            error=f"bad JSON: {type(exc).__name__}",
        )
        return []
