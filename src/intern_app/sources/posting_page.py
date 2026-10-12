"""Reading a posting from its own page, where no board API publishes it.

The ATS APIs in `ats_detail` reach 900 listings. The other 3,300 are on hosts
that publish nothing, and their descriptions are where the degree and the level
actually live — so this fetches the posting page itself.

Three routes are tried in order, cheapest and most reliable first:

1. A host's own JSON endpoint. Workday, SmartRecruiters, Workable and Rippling
   all render their pages from one, and it returns the description as a field
   rather than as markup. Workday alone is 1,076 listings.
2. `schema.org/JobPosting` in a `<script type="application/ld+json">` block.
   That block exists to be read by machines — it is how a posting tells Google
   it is a posting — and iCIMS, Garmin, Waymo and AMD all publish it.
3. Nothing. A page that renders its description in the browser (Apple, Amazon,
   TikTok) is recorded as a miss rather than chased with a headless browser.

Every host is checked against its robots.txt first, every request carries a
User-Agent that says what this is, and no host is asked for two pages inside
`HOST_DELAY` seconds. A 403 is taken as the site saying no and is not retried.

LinkedIn is excluded outright, here and everywhere: LinkedIn data reaches this
app only through the job-alert emails in `linkedin_mail`.
"""

from __future__ import annotations

import json
import re
import sqlite3
import time
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

import httpx

from intern_app import db

SOURCE = "posting_page"

# Says what this is and who runs it, rather than impersonating a browser.
USER_AGENT = "intern-app/0.4 (personal job-search aggregator; one user)"

# Seconds to leave between two requests to the same host.
HOST_DELAY = 1.5

# Hosts this never touches, whatever the rest of the rules say.
NEVER = ("linkedin.com",)

# A Workday url may carry a locale segment before the site name —
# /en-US/magna/job/... — which is not part of the API path.
WORKDAY = re.compile(
    r"https://([^.]+)\.(wd\d+)\.myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?([^/]+)/job/(.+)"
)
SMARTRECRUITERS = re.compile(r"jobs\.smartrecruiters\.com/([^/?#]+)/([^/?#]+)")
WORKABLE = re.compile(r"apply\.workable\.com/([^/?#]+)/j/([^/?#]+)")
RIPPLING = re.compile(r"ats\.rippling\.com/([^/?#]+)/jobs/([^/?#]+)")

JSON_LD = re.compile(r"<script[^>]+application/ld\+json[^>]*>(.*?)</script>", re.S | re.I)
TAGS = re.compile(r"<[^>]+>")
BLANKS = re.compile(r"\n{3,}")


def strip_html(text: str) -> str:
    """Readable plain text from an HTML fragment."""
    from html import unescape

    broken = re.sub(r"<(br|/p|/div|/li|/h\d)[^>]*>", "\n", text, flags=re.IGNORECASE)
    return BLANKS.sub("\n\n", unescape(TAGS.sub("", broken))).strip()


def json_endpoint(url: str) -> tuple[str, str] | None:
    """The (host kind, JSON url) that serves this posting, or None.

    These are the endpoints each site's own page calls to render itself. They
    return the description as a field, so nothing has to be parsed out of
    markup.
    """
    found = WORKDAY.match(url)
    if found:
        tenant, pod, site, rest = found.groups()
        return (
            "workday",
            f"https://{tenant}.{pod}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/job/{rest}",
        )

    found = SMARTRECRUITERS.search(url)
    if found:
        company, posting = found.groups()
        return (
            "smartrecruiters",
            f"https://api.smartrecruiters.com/v1/companies/{company}/postings/{posting}",
        )

    found = WORKABLE.search(url)
    if found:
        account, shortcode = found.groups()
        return (
            "workable",
            f"https://apply.workable.com/api/v1/accounts/{account}/jobs/{shortcode}",
        )

    found = RIPPLING.search(url)
    if found:
        board, job_id = found.groups()
        return (
            "rippling",
            f"https://api.rippling.com/platform/api/ats/v1/board/{board}/jobs/{job_id}",
        )

    return None


def description_from_json(kind: str, payload: dict) -> str:
    """The description field, wherever each endpoint keeps it."""
    if kind == "workday":
        return strip_html(payload.get("jobPostingInfo", {}).get("jobDescription", ""))
    if kind == "smartrecruiters":
        sections = payload.get("jobAd", {}).get("sections", {})
        parts = [
            sections.get(name, {}).get("text", "")
            for name in (
                "companyDescription",
                "jobDescription",
                "qualifications",
                "additionalInformation",
            )
        ]
        return strip_html("\n\n".join(part for part in parts if part))
    if kind == "workable":
        return strip_html(payload.get("description", "") + "\n\n" + payload.get("requirements", ""))
    if kind == "rippling":
        return strip_html(
            payload.get("job", {}).get("description", "") or payload.get("description", "")
        )
    return ""


def description_from_jsonld(html: str) -> str:
    """The description from a schema.org JobPosting block, or "".

    A page carries several ld+json blocks — breadcrumbs, the organisation, the
    posting — so every one is read and only a JobPosting is taken.
    """
    for block in JSON_LD.findall(html):
        try:
            data = json.loads(block.strip())
        except json.JSONDecodeError:
            continue
        for item in data if isinstance(data, list) else [data]:
            if isinstance(item, dict) and "JobPosting" in str(item.get("@type", "")):
                found = item.get("description", "")
                if found:
                    return strip_html(found)
    return ""


def robots_allows(client: httpx.Client, url: str, cache: dict[str, RobotFileParser | None]) -> bool:
    """Whether this host's robots.txt permits fetching this path.

    A host with no robots.txt, or one we cannot read, is treated as allowing it
    — that is what the standard says an absent file means.
    """
    parts = urlsplit(url)
    host = f"{parts.scheme}://{parts.netloc}"
    if host not in cache:
        rules = RobotFileParser()
        try:
            response = client.get(f"{host}/robots.txt", timeout=10)
            if response.status_code == 200:
                rules.parse(response.text.splitlines())
            else:
                rules = None
        except httpx.HTTPError:
            rules = None
        cache[host] = rules
    rules = cache[host]
    return True if rules is None else rules.can_fetch(USER_AGENT, url)


def wait_for_host(host: str, last_seen: dict[str, float]) -> None:
    """Leave `HOST_DELAY` between two requests to the same host."""
    gap = time.monotonic() - last_seen.get(host, 0.0)
    if gap < HOST_DELAY:
        time.sleep(HOST_DELAY - gap)
    last_seen[host] = time.monotonic()


def listings_needing_page(conn: sqlite3.Connection, limit: int = 0) -> list[sqlite3.Row]:
    """Listings with no full text, no board API, and no failed attempt yet."""
    sql = """
        SELECT l.id, l.url FROM listings l
        LEFT JOIN page_misses m ON m.listing_id = l.id
        WHERE l.full_text = 0
          AND m.listing_id IS NULL
          AND l.url LIKE 'http%'
          AND l.url NOT LIKE '%linkedin.com%'
          AND l.url NOT LIKE '%greenhouse.io%'
          AND l.url NOT LIKE '%lever.co%'
          AND l.url NOT LIKE '%ashbyhq.com%'
          -- Adzuna's land/ad links are a redirector that refuses bots, and we
          -- already hold what its API gives us.
          AND l.url NOT LIKE '%adzuna.com%'
        ORDER BY l.first_seen DESC, l.id DESC
    """
    if limit:
        return conn.execute(sql + " LIMIT ?", (limit,)).fetchall()
    return conn.execute(sql).fetchall()


def record_miss(conn: sqlite3.Connection, listing_id: int, host: str, reason: str) -> None:
    """Remember that this page could not be read, and why."""
    conn.execute(
        """
        INSERT INTO page_misses (listing_id, host, reason, tried_at) VALUES (?, ?, ?, ?)
        ON CONFLICT (listing_id) DO UPDATE SET
            host = excluded.host, reason = excluded.reason, tried_at = excluded.tried_at
        """,
        (listing_id, host, reason, db.utcnow()),
    )


def collect_pages(conn: sqlite3.Connection, *, limit: int = 0) -> dict[str, int]:
    """Read every posting page in reach, storing the description it carries."""
    from intern_app.sources.ats_detail import store_description

    found = {"tried": 0, "stored": 0, "blocked": 0, "refused": 0, "empty": 0, "failed": 0}
    robots: dict[str, RobotFileParser | None] = {}
    last_seen: dict[str, float] = {}

    with httpx.Client(
        timeout=25, follow_redirects=True, headers={"User-Agent": USER_AGENT}
    ) as client:
        for row in listings_needing_page(conn, limit):
            url = row["url"]
            host = urlsplit(url).hostname or ""
            if any(name in host for name in NEVER):
                continue
            found["tried"] += 1

            target = json_endpoint(url)
            fetch_url = target[1] if target else url

            if not robots_allows(client, fetch_url, robots):
                found["blocked"] += 1
                record_miss(conn, row["id"], host, "robots.txt")
                continue

            wait_for_host(host, last_seen)
            try:
                response = client.get(fetch_url)
            except httpx.HTTPError as exc:
                found["failed"] += 1
                record_miss(conn, row["id"], host, type(exc).__name__)
                db.record_api_call(
                    conn, source=SOURCE, endpoint=fetch_url, ok=False, error=type(exc).__name__
                )
                continue

            db.record_api_call(
                conn,
                source=SOURCE,
                endpoint=fetch_url,
                status_code=response.status_code,
                ok=response.status_code == 200,
            )

            if response.status_code in (401, 403, 429):
                found["refused"] += 1
                record_miss(conn, row["id"], host, f"HTTP {response.status_code}")
                continue
            if response.status_code != 200:
                found["failed"] += 1
                record_miss(conn, row["id"], host, f"HTTP {response.status_code}")
                continue

            text = ""
            if target:
                try:
                    text = description_from_json(target[0], response.json())
                except json.JSONDecodeError:
                    text = ""
            if not text:
                text = description_from_jsonld(response.text)

            if len(text) > 200:
                store_description(conn, row["id"], text)
                found["stored"] += 1
            else:
                found["empty"] += 1
                record_miss(conn, row["id"], host, "no description on the page")
    return found
