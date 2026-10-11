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
from pydantic import BaseModel

from intern_app import board, profile

router = APIRouter(prefix="/api")


def open_db() -> sqlite3.Connection:
    """A connection per request. SQLite is local and this is one user."""
    from intern_app import db

    return db.connect()


def as_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    """Rows as plain dicts, which is what FastAPI can serialize."""
    return [dict(row) for row in rows]


@router.get("/listings")
def read_listings(
    industry: str = "",
    days: int = 0,
    sort: str = board.DEFAULT_SORT,
    page: int = 1,
    per_page: int = board.DEFAULT_PER_PAGE,
    role: Annotated[list[str] | None, Query()] = None,
    level: Annotated[list[str] | None, Query()] = None,
) -> dict[str, Any]:
    """One page of the dashboard: listings I have not acted on."""
    page = max(1, page)
    per_page = min(max(1, per_page), 200)
    roles = [name for name in (role or []) if name.strip()]
    levels = [name for name in (level or []) if name.strip()]

    conn = open_db()
    try:
        total = board.count_new(conn, industry=industry, days=days, roles=roles, levels=levels)
        rows = board.list_new(
            conn,
            industry=industry,
            days=days,
            roles=roles,
            levels=levels,
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
            conn, text=q, industry=industry, status=status, page=page, per_page=per_page
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
