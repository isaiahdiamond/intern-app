"""Industry classification, per company.

The Muse returns no industry — its `categories` field is a job function — so
industry has to be inferred. It is a property of the company rather than the
posting, so one call covers every listing that company has, now and later.
"""

from __future__ import annotations

import sqlite3

from pydantic import BaseModel

from intern_app import db
from intern_app.llm.client import call_structured, load_prompt
from intern_app.roles import INDUSTRIES

UNKNOWN = "Unknown"

# Classifying many companies in one call is far cheaper than one call each, but
# a huge list invites a truncated reply, so batches stay small.
BATCH_SIZE = 25


class CompanyIndustry(BaseModel):
    company: str
    industry: str


class Classifications(BaseModel):
    companies: list[CompanyIndustry]


def classify_companies(conn: sqlite3.Connection, names: list[str]) -> dict[str, str]:
    """Classify each company and store the result. Returns what was assigned.

    An industry the model invents is rejected rather than stored, because the
    dashboard ranks against the fixed list and an unknown value would sort as
    if the user had never heard of it.
    """
    allowed = {name.lower(): name for name in INDUSTRIES}
    assigned: dict[str, str] = {}

    for start in range(0, len(names), BATCH_SIZE):
        batch = names[start : start + BATCH_SIZE]
        prompt = load_prompt(
            "classify_industry",
            industries="\n".join(f"- {name}" for name in INDUSTRIES),
            companies="\n".join(f"- {name}" for name in batch),
        )
        result = call_structured(
            conn,
            prompt_name="classify_industry",
            prompt=prompt,
            output_model=Classifications,
        )

        replied = {item.company.strip().lower(): item.industry.strip() for item in result.companies}
        for name in batch:
            answer = replied.get(name.strip().lower())
            if answer is None:
                # Left unclassified rather than marked Unknown, so the next run
                # retries it instead of writing off a company the model skipped.
                continue
            industry = allowed.get(answer.lower(), UNKNOWN)
            db.set_company_industry(conn, name, industry)
            assigned[name] = industry

    return assigned
