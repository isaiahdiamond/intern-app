"""The "Other" button: turn what a student describes into role chips."""

from __future__ import annotations

import sqlite3

from pydantic import BaseModel, Field

from intern_app.llm.client import call_structured, load_prompt

MAX_SUGGESTIONS = 8


class SuggestedRoles(BaseModel):
    """What the model returns. Validated, so a malformed reply fails loudly."""

    roles: list[str] = Field(default_factory=list)


def suggest_roles(conn: sqlite3.Connection, *, major: str, interests: str) -> list[str]:
    """Role titles matching a free-text description, as new chips to select.

    Trims to `MAX_SUGGESTIONS` and drops duplicates and blanks, because the
    prompt asks for a bounded list but the reply is not guaranteed to honor it.
    """
    prompt = load_prompt("suggest_roles", major=major, interests=interests)
    result = call_structured(
        conn,
        prompt_name="suggest_roles",
        prompt=prompt,
        output_model=SuggestedRoles,
    )

    seen: list[str] = []
    for role in result.roles:
        cleaned = role.strip()
        if cleaned and cleaned not in seen:
            seen.append(cleaned)
    return seen[:MAX_SUGGESTIONS]
