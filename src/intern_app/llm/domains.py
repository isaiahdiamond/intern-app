"""Working out which website belongs to a company.

The apply url answers this for about one company in six — the rest post through
greenhouse, workday or ashby, whose hosts say nothing about the company. A
name is not a domain and the obvious guess is often somebody else's site:
"Multiply Labs" is multiplylabs.com, while multiply.com is a different company
altogether, and a wrong logo is worse than no logo. So this asks Claude, and
keeps only the answers it says it is sure of.
"""

from __future__ import annotations

import sqlite3

from pydantic import BaseModel

from intern_app.llm.client import call_structured, load_prompt

# Names are short, so a batch can be much larger than the title batches. Fifty
# names at two fields each leaves plenty of room under the ceiling.
BATCH_SIZE = 50
MAX_TOKENS = 4000


class CompanyDomain(BaseModel):
    company: str
    domain: str = ""
    confident: bool = False


class CompanyDomains(BaseModel):
    companies: list[CompanyDomain]


def clean_domain(domain: str) -> str:
    """A bare lowercase hostname, however the reply was written."""
    text = domain.strip().lower()
    for prefix in ("https://", "http://"):
        text = text.removeprefix(prefix)
    text = text.removeprefix("www.").split("/")[0].strip(".")
    return text if "." in text and " " not in text else ""


def resolve_domains(conn: sqlite3.Connection, names: list[str]) -> dict[str, str]:
    """Map each company name to its domain, leaving out the unsure ones.

    A name Claude is not confident about is simply absent from the result, so
    the caller records a miss for it rather than fetching somebody else's logo.
    """
    found: dict[str, str] = {}

    for start in range(0, len(names), BATCH_SIZE):
        batch = names[start : start + BATCH_SIZE]
        listed = "\n".join(batch)
        prompt = load_prompt("company_domain", companies=listed)

        result = call_structured(
            conn,
            prompt_name="company_domain",
            prompt=prompt,
            output_model=CompanyDomains,
            max_tokens=MAX_TOKENS,
        )

        wanted = set(batch)
        for answer in result.companies:
            if answer.company not in wanted or not answer.confident:
                continue
            domain = clean_domain(answer.domain)
            if domain:
                found[answer.company] = domain

    return found
