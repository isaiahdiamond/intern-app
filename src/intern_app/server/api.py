"""JSON endpoints for the React frontend in `web/`.

Everything here is a thin wrapper over `board` and `profile`: the SQL, the
ordering and the status rules live there, and this module only turns rows into
JSON. Vite proxies `/api` to this app in development, so the frontend never
needs a base URL.
"""

from __future__ import annotations

import sqlite3
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel

from intern_app import board, icons, profile

router = APIRouter(prefix="/api")


def open_db() -> sqlite3.Connection:
    """A connection per request. SQLite is local and this is one user."""
    from intern_app import db

    return db.connect()


def as_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    """Rows as plain dicts, which is what FastAPI can serialize."""
    return [dict(row) for row in rows]


def profile_filters(conn) -> dict[str, list[str]]:
    """The roles, levels and degrees the stored profile narrows a list to.

    Empty lists mean "do not filter on this", so a profile that has not said
    what it wants still sees everything rather than nothing.
    """
    saved = profile.load_profile(conn) or {}
    return {
        "roles": list(saved.get("roles", [])),
        "levels": list(saved.get("seeking", [])),
        "educations": profile.degrees_open_to(saved.get("education", "")),
    }


@router.get("/listings")
def read_listings(
    industry: str = "",
    days: int = 0,
    sort: str = board.DEFAULT_SORT,
    page: int = 1,
    per_page: int = board.DEFAULT_PER_PAGE,
    role: Annotated[list[str] | None, Query()] = None,
    level: Annotated[list[str] | None, Query()] = None,
    education: Annotated[list[str] | None, Query()] = None,
    match_profile: bool = False,
) -> dict[str, Any]:
    """One page of the dashboard: listings I have not acted on.

    `match_profile` narrows to what the profile says it wants — its roles, the
    levels it is looking for, and the degree requirements it is open to. The
    dashboard asks for that; the All listings page does not, because browsing
    everything is the point of it.
    """
    page = max(1, page)
    per_page = min(max(1, per_page), 200)
    roles = [name for name in (role or []) if name.strip()]
    levels = [name for name in (level or []) if name.strip()]
    educations = [name for name in (education or []) if name.strip()]

    conn = open_db()
    try:
        if match_profile:
            wanted = profile_filters(conn)
            roles = roles or wanted["roles"]
            levels = levels or wanted["levels"]
            educations = educations or wanted["educations"]
        total = board.count_new(
            conn,
            industry=industry,
            days=days,
            roles=roles,
            levels=levels,
            educations=educations,
        )
        rows = board.list_new(
            conn,
            industry=industry,
            days=days,
            roles=roles,
            levels=levels,
            educations=educations,
            sort=sort,
            page=page,
            per_page=per_page,
        )
        return {
            "listings": as_dicts(rows),
            "total": total,
            "page": page,
            "per_page": per_page,
            "has_more": page * per_page < total,
        }
    finally:
        conn.close()


@router.get("/search")
def read_search(
    q: str = "",
    industry: str = "",
    status: str = "",
    sort: str = board.DEFAULT_SORT,
    page: int = 1,
    per_page: int = board.DEFAULT_PER_PAGE,
) -> dict[str, Any]:
    """One page of every stored listing, whatever its status."""
    page = max(1, page)
    per_page = min(max(1, per_page), 200)

    conn = open_db()
    try:
        total = board.count_search(conn, text=q, industry=industry, status=status)
        rows = board.search_listings(
            conn,
            text=q,
            industry=industry,
            status=status,
            sort=sort,
            page=page,
            per_page=per_page,
        )
        return {
            "listings": as_dicts(rows),
            "total": total,
            "page": page,
            "per_page": per_page,
            "has_more": page * per_page < total,
        }
    finally:
        conn.close()


@router.get("/tracker")
def read_tracker() -> dict[str, Any]:
    """Everything I have acted on, each row carrying its own status history."""
    conn = open_db()
    try:
        rows = board.list_tracked(conn)
        listings = []
        for row in rows:
            entry = dict(row)
            entry["history"] = as_dicts(board.history_for(conn, row["id"]))
            listings.append(entry)
        return {"listings": listings, "counts": board.status_counts(conn)}
    finally:
        conn.close()


class StatusChange(BaseModel):
    listing_id: int
    status: str


@router.post("/status")
def write_status(change: StatusChange) -> dict[str, Any]:
    """Move a listing to a new status and return the fresh badge counts."""
    conn = open_db()
    try:
        try:
            board.set_status(conn, change.listing_id, change.status)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"counts": board.status_counts(conn)}
    finally:
        conn.close()


@router.get("/filters")
def read_filters() -> dict[str, Any]:
    """Everything the sidebar and filter bar need to render themselves."""
    conn = open_db()
    try:
        return {
            "industries": board.known_industries(conn),
            "industry_counts": board.new_counts_by_industry(conn),
            "status_counts": board.status_counts(conn),
            "level_counts": board.level_counts(conn),
            "education_counts": board.education_counts(conn),
            "roles": profile.load_role_names(conn),
            "sorts": list(board.SORT_ORDERS),
            "statuses": list(board.ACTIVE),
        }
    finally:
        conn.close()


@router.get("/profile")
def read_profile() -> dict[str, Any]:
    """The onboarding answers, plus whether onboarding is done at all."""
    conn = open_db()
    try:
        return {
            "onboarded": profile.is_onboarded(conn),
            "profile": profile.load_profile(conn),
        }
    finally:
        conn.close()


class ManualListing(BaseModel):
    title: str
    company: str
    location: str = ""
    url: str = ""
    posted_at: str = ""
    status: str = "applied"
    notes: str = ""


@router.post("/manual")
def write_manual_listing(entry: ManualListing) -> dict[str, Any]:
    """Add a job I found outside the app, straight into the tracker."""
    conn = open_db()
    try:
        try:
            listing_id = board.add_manual_listing(
                conn,
                title=entry.title,
                company=entry.company,
                location=entry.location,
                url=entry.url,
                posted_at=entry.posted_at,
                status=entry.status,
                notes=entry.notes,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"listing_id": listing_id, "counts": board.status_counts(conn)}
    finally:
        conn.close()


@router.get("/icon/{company}")
def read_icon(company: str) -> Response:
    """A company's cached favicon, or 404 so the row draws its fallback tile.

    The bytes were fetched once by `intern-app icons` and stored locally, so
    rendering the board makes no third-party request and tells nobody which
    companies are on it.
    """
    conn = open_db()
    try:
        row = icons.read_icon(conn, company)
    finally:
        conn.close()

    if row is None or row["image"] is None:
        raise HTTPException(status_code=404, detail="no icon for that company")
    return Response(
        content=row["image"],
        media_type=row["content_type"] or "image/x-icon",
        headers={"Cache-Control": "public, max-age=86400"},
    )


class ProfileEdit(BaseModel):
    school: str = ""
    major: str = ""
    education: str = ""
    seeking: list[str] = []
    roles: list[str] = []
    industries: list[str] = []


@router.post("/profile")
def write_profile(edit: ProfileEdit) -> dict[str, Any]:
    """Save the profile. This is what the dashboard then filters down to."""
    conn = open_db()
    try:
        saved = profile.load_profile(conn) or {}
        known = set(saved.get("roles", []))
        try:
            profile.save_profile(
                conn,
                school=edit.school or saved.get("school", ""),
                major=edit.major or saved.get("major", ""),
                education=edit.education,
                seeking=edit.seeking,
                # A role that was already on the profile keeps its origin; a new
                # one typed here was chosen by hand, not suggested.
                roles=[(name, "chip" if name in known else "llm_suggested") for name in edit.roles],
                industries=edit.industries or list(saved.get("industries", [])),
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return {"onboarded": profile.is_onboarded(conn), "profile": profile.load_profile(conn)}
    finally:
        conn.close()


@router.get("/options")
def read_options() -> dict[str, Any]:
    """The fixed choices the profile form offers."""
    return {
        "degrees": [
            {"key": "undergrad", "label": "Bachelor's"},
            {"key": "masters", "label": "Master's"},
            {"key": "phd", "label": "PhD"},
        ],
        "seeking": [
            {"key": "intern", "label": "Internship"},
            {"key": "coop", "label": "Co-op"},
            {"key": "new_grad", "label": "New grad"},
        ],
    }
