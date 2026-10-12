"""Company websites and their favicons, for the logo tile on every row.

A listing's apply url is usually not the company: `job-boards.greenhouse.io`,
`nvidia.wd5.myworkdayjobs.com` and `jobs.ashbyhq.com` are applicant tracking
systems, and 1,052 of the 1,265 stored companies have no company-owned host
anywhere in their listings. So the domain is worked out in two steps — take it
from the apply url when the host really is the company's, and ask Claude for
the rest — and then one favicon is fetched per company and cached.

The fetch happens here, on the server, once per company. The frontend only ever
reads `/api/icon/<company>` from its own origin, so opening the board does not
tell anyone else which companies you are looking at.
"""

from __future__ import annotations

import sqlite3
from urllib.parse import urlsplit

import httpx

from intern_app import db

# Where the icon comes from. It answers for a domain it knows and 404s for one
# it does not, which is exactly the yes-or-no a guessed domain needs.
ICON_URL = "https://icons.duckduckgo.com/ip3/{domain}.ico"

SOURCE = "favicons"

# Hosts that belong to a job board or an applicant tracking system rather than
# to the company doing the hiring. A url on one of these says nothing about the
# company's own website.
ATS_HOSTS = (
    "greenhouse.io",
    "lever.co",
    "ashbyhq.com",
    "myworkdayjobs.com",
    "smartrecruiters.com",
    "workable.com",
    "icims.com",
    "rippling.com",
    "oraclecloud.com",
    "taleo.net",
    "successfactors.com",
    "bamboohr.com",
    "jobvite.com",
    "paylocity.com",
    "dayforcehcm.com",
    "applytojob.com",
    "breezy.hr",
    "recruitee.com",
    "teamtailor.com",
    "phenompeople.com",
    "eightfold.ai",
    "avature.net",
    "adzuna.com",
    "themuse.com",
    "linkedin.com",
    "jobright.ai",
    "workatastartup.com",
    "ripplematch.com",
    "simplify.jobs",
    "usajobs.gov",
    "indeed.com",
    "glassdoor.com",
    "ziprecruiter.com",
    "github.com",
    "github.io",
    "notion.site",
    "google.com",
    "airtable.com",
    "builtin.com",
    "wellfound.com",
    "handshake.com",
    "joinhandshake.com",
)

# Second-level domains that are part of a country suffix rather than a name, so
# "careers.bbc.co.uk" keeps three labels while "jobs.apple.com" keeps two.
PUBLIC_SECOND_LEVELS = ("co", "com", "org", "net", "gov", "ac", "edu")


def registrable(host: str) -> str:
    """The company-identifying part of a hostname, without the subdomain."""
    labels = host.lower().removeprefix("www.").strip(".").split(".")
    if len(labels) < 2:
        return ""
    if len(labels) >= 3 and labels[-2] in PUBLIC_SECOND_LEVELS and len(labels[-1]) == 2:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


def is_ats(host: str) -> bool:
    """True when a host belongs to a job board rather than to a company."""
    host = host.lower()
    return any(host == name or host.endswith("." + name) for name in ATS_HOSTS)


def domain_from_urls(urls: list[str]) -> str:
    """A company's own domain taken from its apply links, or "" if none is.

    Tried before asking Claude, because an apply link on the company's own site
    is evidence rather than a guess. A career subdomain such as
    `lifeattiktok.com` counts: its favicon is the company's logo.
    """
    for url in urls:
        host = urlsplit(url).hostname or ""
        if host and not is_ats(host):
            found = registrable(host)
            if found:
                return found
    return ""


def companies_needing_icon(conn: sqlite3.Connection, limit: int = 0) -> list[sqlite3.Row]:
    """Companies we hold listings for and have never looked an icon up for.

    Each row carries the company's apply urls, so the caller can read a domain
    off them without a second query.
    """
    sql = """
        SELECT l.company AS company, group_concat(l.url, char(10)) AS urls
        FROM listings l
        LEFT JOIN company_icons i ON i.company = l.company
        WHERE l.company <> '' AND i.company IS NULL
        GROUP BY l.company
        ORDER BY COUNT(*) DESC
    """
    if limit:
        return conn.execute(sql + " LIMIT ?", (limit,)).fetchall()
    return conn.execute(sql).fetchall()


def save_icon(
    conn: sqlite3.Connection,
    *,
    company: str,
    domain: str,
    domain_from: str,
    image: bytes | None = None,
    content_type: str = "",
    ok: bool = False,
    error: str = "",
) -> None:
    """Store what we found for a company, including having found nothing."""
    conn.execute(
        """
        INSERT INTO company_icons
            (company, domain, domain_from, image, content_type, fetched_at, ok, error)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (company) DO UPDATE SET
            domain = excluded.domain,
            domain_from = excluded.domain_from,
            image = excluded.image,
            content_type = excluded.content_type,
            fetched_at = excluded.fetched_at,
            ok = excluded.ok,
            error = excluded.error
        """,
        (company, domain, domain_from, image, content_type, db.utcnow(), int(ok), error),
    )


def read_icon(conn: sqlite3.Connection, company: str) -> sqlite3.Row | None:
    """The cached icon for a company, or None if there is not one."""
    return conn.execute(
        "SELECT image, content_type FROM company_icons WHERE company = ? AND ok = 1",
        (company,),
    ).fetchone()


def fetch_icon(
    conn: sqlite3.Connection, client: httpx.Client, domain: str
) -> httpx.Response | None:
    """Ask the icon service for one domain, recording the call either way."""
    try:
        response = client.get(ICON_URL.format(domain=domain))
    except httpx.HTTPError as exc:
        db.record_api_call(
            conn,
            source=SOURCE,
            endpoint=ICON_URL.format(domain=domain),
            ok=False,
            error=type(exc).__name__,
        )
        return None
    db.record_api_call(
        conn,
        source=SOURCE,
        endpoint=ICON_URL.format(domain=domain),
        status_code=response.status_code,
        ok=response.status_code == 200,
    )
    return response


def collect_icons(
    conn: sqlite3.Connection,
    *,
    limit: int = 0,
    domains: dict[str, str] | None = None,
) -> dict[str, int]:
    """Fetch and cache one favicon per company that does not have one yet.

    `domains` maps a company to a domain worked out elsewhere — in practice by
    `llm.domains` — and is used for any company whose apply links are all ATS
    urls. A company with no domain from either route is recorded as a miss, so
    it is not looked up again on the next run.
    """
    found = {"companies": 0, "icons": 0, "no_domain": 0, "no_icon": 0}
    supplied = domains or {}

    rows = companies_needing_icon(conn, limit)
    with httpx.Client(timeout=15, follow_redirects=True) as client:
        for row in rows:
            company = row["company"]
            found["companies"] += 1

            domain = domain_from_urls((row["urls"] or "").split("\n"))
            domain_from = "url" if domain else "claude"
            if not domain:
                domain = supplied.get(company, "")

            if not domain:
                found["no_domain"] += 1
                save_icon(conn, company=company, domain="", domain_from="", error="no domain")
                continue

            response = fetch_icon(conn, client, domain)
            if response is None:
                found["no_icon"] += 1
                save_icon(
                    conn,
                    company=company,
                    domain=domain,
                    domain_from=domain_from,
                    error="request failed",
                )
            elif response.status_code == 200 and response.content:
                found["icons"] += 1
                save_icon(
                    conn,
                    company=company,
                    domain=domain,
                    domain_from=domain_from,
                    image=response.content,
                    content_type=response.headers.get("content-type", "image/x-icon"),
                    ok=True,
                )
            else:
                found["no_icon"] += 1
                save_icon(
                    conn,
                    company=company,
                    domain=domain,
                    domain_from=domain_from,
                    error=f"HTTP {response.status_code}",
                )
    return found
