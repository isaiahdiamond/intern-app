"""The local web app. Phase 1 serves onboarding and a page showing the answers.

Form bodies are parsed with `read_form` below rather than FastAPI's `Form(...)`
parameters or Starlette's `request.form()`. Both of those need the
`python-multipart` package — `request.form()` asserts on it for every content
type, not only multipart — and CLAUDE.md says no new dependency without asking.
An urlencoded body is a few lines of stdlib. Phase 6 adds resume upload, which
is genuinely multipart and will need that package asked for then.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from urllib.parse import parse_qs

import anthropic
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from intern_app import board, db, profile, roles
from intern_app.llm import client, suggest

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

app = FastAPI(title="intern-app")


async def read_form(request: Request) -> dict[str, list[str]]:
    """Parse an urlencoded form body into a name -> values mapping.

    Every value is a list, because the role and industry checkboxes repeat a
    name. `one()` pulls a single value back out.
    """
    # errors="replace" rather than a 500 on a non-UTF-8 body.
    body = (await request.body()).decode("utf-8", errors="replace")
    return parse_qs(body, keep_blank_values=True)


def first_value(form: dict[str, list[str]], name: str, default: str = "") -> str:
    """The first value for `name`, trimmed, or `default` when absent."""
    values = form.get(name) or []
    return values[0].strip() if values else default


def open_db() -> sqlite3.Connection:
    """A connection per request. SQLite is local and this is one user."""
    return db.connect()


@app.get("/", response_class=HTMLResponse)
def show_dashboard(request: Request, industry: str = "", days: int = 0):
    """New listings for my roles, best-matching industry first."""
    conn = open_db()
    try:
        if not profile.is_onboarded(conn):
            return RedirectResponse("/onboarding")
        return TEMPLATES.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "tab": "dashboard",
                "listings": board.list_new(conn, industry=industry, days=days),
                "industries": board.known_industries(conn),
                "counts": board.status_counts(conn),
                "chosen_industry": industry,
                "chosen_days": days,
                "statuses": board.ACTIVE,
                "profile": profile.load_profile(conn),
            },
        )
    finally:
        conn.close()


@app.get("/tracker", response_class=HTMLResponse)
def show_tracker(request: Request):
    """Everything I have acted on, grouped by where it is in the pipeline."""
    conn = open_db()
    try:
        rows = board.list_tracked(conn)
        return TEMPLATES.TemplateResponse(
            request=request,
            name="tracker.html",
            context={
                "tab": "tracker",
                "rows": rows,
                "histories": {row["id"]: board.history_for(conn, row["id"]) for row in rows},
                "counts": board.status_counts(conn),
                "statuses": board.ACTIVE,
            },
        )
    finally:
        conn.close()


@app.get("/search", response_class=HTMLResponse)
def show_search(request: Request, q: str = "", industry: str = "", status: str = ""):
    """Search every stored listing, not just the new ones."""
    conn = open_db()
    try:
        return TEMPLATES.TemplateResponse(
            request=request,
            name="search.html",
            context={
                "tab": "search",
                "listings": board.search_listings(conn, text=q, industry=industry, status=status),
                "industries": board.known_industries(conn),
                "counts": board.status_counts(conn),
                "q": q,
                "chosen_industry": industry,
                "chosen_status": status,
                "statuses": board.ACTIVE,
            },
        )
    finally:
        conn.close()


@app.get("/profile", response_class=HTMLResponse)
def show_profile(request: Request):
    """My onboarding answers, with a link back to edit them."""
    conn = open_db()
    try:
        if not profile.is_onboarded(conn):
            return RedirectResponse("/onboarding")
        return TEMPLATES.TemplateResponse(
            request=request,
            name="saved.html",
            context={
                "tab": "profile",
                "profile": profile.load_profile(conn),
                "counts": board.status_counts(conn),
            },
        )
    finally:
        conn.close()


@app.post("/status")
async def change_status(request: Request):
    """Move a listing to a new status, then return to where the click came from."""
    form = await read_form(request)
    listing_id = int(first_value(form, "listing_id") or 0)
    status = first_value(form, "status")
    back = first_value(form, "back") or "/"

    conn = open_db()
    try:
        board.set_status(conn, listing_id, status)
    finally:
        conn.close()
    return RedirectResponse(back, status_code=303)


@app.get("/onboarding", response_class=HTMLResponse)
def show_step_one(request: Request):
    """Questions 1 and 2: school and major."""
    conn = open_db()
    try:
        saved = profile.load_profile(conn) or {}
    finally:
        conn.close()
    return TEMPLATES.TemplateResponse(
        request=request,
        name="step1.html",
        context={"school": saved.get("school", ""), "major": saved.get("major", "")},
    )


@app.post("/onboarding/roles", response_class=HTMLResponse)
async def show_step_two(request: Request):
    """Questions 3 and 4: role chips for the major, then ranked industries.

    School and major ride along as hidden fields, so there is no session to
    keep. The Other button posts back here with suggestions appended.
    """
    form = await read_form(request)
    school = first_value(form, "school")
    major = first_value(form, "major")

    if not major:
        return RedirectResponse("/onboarding", status_code=303)

    chips = list(roles.roles_for_major(major))
    suggested = [value.strip() for value in form.get("suggested", []) if value.strip()]
    selected = [value.strip() for value in form.get("roles", []) if value.strip()]
    ranked = [name for name in first_value(form, "industry_order").split("|") if name.strip()]
    error = ""

    # Coming from step 1 there is nothing ticked yet, so fall back to whatever
    # the profile already holds — that is what makes "Edit answers" an edit
    # rather than a blank restart. A post from step 2 is trusted as-is, so
    # unticking everything stays unticked.
    if not first_value(form, "from_step2"):
        conn = open_db()
        try:
            saved = profile.load_profile(conn) or {}
        finally:
            conn.close()
        selected = list(saved.get("roles", []))
        ranked = list(saved.get("industries", []))
        for role in selected:
            if role not in chips and role not in suggested:
                suggested.append(role)

    if first_value(form, "action") == "suggest":
        interests = first_value(form, "interests")
        if not interests:
            error = "Say a little about what you are looking for first."
        elif not client.have_api_key():
            error = "Suggestions need ANTHROPIC_API_KEY in .env. Pick from the chips instead."
        else:
            conn = open_db()
            try:
                new_roles = suggest.suggest_roles(conn, major=major, interests=interests)
            except (anthropic.APIError, client.UnusableReplyError, ValidationError) as exc:
                # The call is already logged by call_structured; the page still
                # has to render, so report the kind of failure and carry on.
                new_roles = []
                error = f"Could not get suggestions: {type(exc).__name__}"
            finally:
                conn.close()
            if not new_roles and not error:
                error = "No roles came back for that. Try describing it differently."
            for role in new_roles:
                if role not in suggested and role not in chips:
                    suggested.append(role)

    return TEMPLATES.TemplateResponse(
        request=request,
        name="step2.html",
        context={
            "school": school,
            "major": major,
            "chips": chips,
            "suggested": suggested,
            "industries": roles.INDUSTRIES,
            "selected": selected,
            "ranked": ranked,
            "error": error,
            "llm_available": client.have_api_key(),
        },
    )


@app.post("/onboarding/save")
async def save_onboarding(request: Request):
    """Write the profile and go to the answers page."""
    form = await read_form(request)
    major = first_value(form, "major")
    chips = set(roles.roles_for_major(major))
    chosen = [value.strip() for value in form.get("roles", []) if value.strip()]

    conn = open_db()
    try:
        profile.save_profile(
            conn,
            school=first_value(form, "school"),
            major=major,
            # A role not in this major's chip list came from the LLM.
            roles=[(role, "chip" if role in chips else "llm_suggested") for role in chosen],
            # Click order is the preference order; the hidden field carries it.
            industries=[
                name.strip()
                for name in first_value(form, "industry_order").split("|")
                if name.strip()
            ],
        )
    finally:
        conn.close()
    return RedirectResponse("/", status_code=303)
