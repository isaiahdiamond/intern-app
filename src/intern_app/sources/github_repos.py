"""Community internship repos on GitHub, as discovery sources.

These are lists, not postings: they give a title, a company, a location and an
apply link, so every listing is `full_text=False` and none goes to requirement
extraction. Their value is coverage — the four JSON repos alone carry thousands
of active roles that The Muse never sees.

Two shapes, both confirmed against the live files:

- Four repos publish `.github/scripts/listings.json`, a flat array sharing one
  schema: `title`, `company_name`, `locations`, `url`, `active`, `is_visible`,
  `date_posted`. That is preferred wherever it exists.
- Four publish only a README with pipe tables, in three different column
  layouts, so each gets its own row parser.

Everything is fetched from raw.githubusercontent.com and polled at most twice a
day, which the quota floor enforces.
"""

from __future__ import annotations

import html
import re
import sqlite3
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

import httpx

from intern_app import db
from intern_app.sources import quota
from intern_app.sources.ats_links import remember_board
from intern_app.sources.base import Listing, normalize
from intern_app.sources.role_match import title_matches_role
from intern_app.sources.us_filter import is_us_or_remote

SOURCE = "github_repos"
RAW = "https://raw.githubusercontent.com"

# Marks a listing the repo has closed. Checked against the whole row.
CLOSED_MARKS = ("🔒", "closed", "no longer accepting")


@dataclass(frozen=True)
class Repo:
    """One tracked repo and how to read it."""

    name: str
    branch: str
    kind: str  # "json" or the name of a README row parser
    usa_only: bool = False


REPOS: tuple[Repo, ...] = (
    Repo("SimplifyJobs/Summer2027-Internships", "dev", "json"),
    Repo("SimplifyJobs/New-Grad-Positions", "dev", "json"),
    Repo("vanshb03/Summer2027-Internships", "dev", "json"),
    Repo("vanshb03/New-Grad-2027", "dev", "json"),
    Repo("speedyapply/2027-SWE-College-Jobs", "main", "speedyapply", usa_only=True),
    Repo("speedyapply/2027-AI-College-Jobs", "main", "speedyapply", usa_only=True),
    Repo("jobright-ai/2026-Software-Engineer-Internship", "master", "jobright"),
    Repo(
        "zshah101/Automated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships",
        "main",
        "zshah",
    ),
    Repo("resumax/tech-internships", "main", "resumax"),
)

JSON_PATH = ".github/scripts/listings.json"
README_PATH = "README.md"

# Zero-width characters appear inside titles in at least one repo
# ("Cybersecur​ity"), which breaks every word match until they are gone.
INVISIBLE = re.compile("[\u200b-\u200f\u2060\ufeff]")

MARKDOWN_LINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
HTML_LINK = re.compile(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>', re.I | re.S)
TAGS = re.compile(r"<[^>]+>")


# Emoji, arrows, and pictographs, which these READMEs use heavily as status
# markers. Deliberately narrow: an earlier `ord(ch) > 0x2100` test also deleted
# CJK, and anything that broad risks eating real characters out of a name.
EMOJI_RANGES = (
    (0x2190, 0x2BFF),  # arrows, dingbats, misc symbols
    (0x2E00, 0x2E7F),  # supplemental punctuation
    (0x1F000, 0x1FAFF),  # emoji proper
    (0xFE00, 0xFE0F),  # variation selectors
    (0x1F1E6, 0x1F1FF),  # regional indicators (flags)
)

BREAK_TAG = re.compile(r"(?i)<\s*br\s*/?\s*>")


def _is_emoji(ch: str) -> bool:
    point = ord(ch)
    return any(low <= point <= high for low, high in EMOJI_RANGES)


def clean_cell(cell: str) -> str:
    """A table cell as plain text: no markup, no emoji noise, no invisibles.

    `<br>` becomes a separator rather than vanishing, because several repos put
    multiple locations in one cell and joining them produced "SF, CANY, NY".
    Non-breaking spaces become real spaces for the same reason: deleting them
    turned "Software&nbsp;Engineer" into "SoftwareEngineer", which no role
    matcher can read.
    """
    text = INVISIBLE.sub("", cell)
    text = BREAK_TAG.sub("; ", text)
    text = MARKDOWN_LINK.sub(r"\1", text)
    text = TAGS.sub("", text)
    text = html.unescape(text)
    text = "".join(" " if ch.isspace() else ch for ch in text)
    text = "".join(ch for ch in text if ch.isprintable() and not _is_emoji(ch))
    return " ".join(text.split()).strip(" *|;,")


def first_link(cell: str) -> str:
    """The first URL in a cell, markdown or HTML."""
    found = MARKDOWN_LINK.search(cell)
    if found:
        return found.group(2).strip()
    found = HTML_LINK.search(cell)
    if found:
        return found.group(1).strip()
    return ""


def apply_link(cells: list[str]) -> str:
    """The apply URL on a row, found by scanning rather than by column index.

    Column positions are not stable: speedyapply publishes both a six-column
    layout with Salary and a five-column one without, which moves the Posting
    link. Indexing a fixed column silently dropped 656 of its 772 rows. The
    first cell is skipped because it holds the company's own website.
    """
    for cell in cells[1:]:
        url = first_link(cell)
        if url.startswith("http"):
            return url
    return ""


def is_closed(row: str) -> bool:
    lowered = row.lower()
    return any(mark in lowered for mark in CLOSED_MARKS)


def all_rows(markdown: str) -> list[list[str]]:
    """Every pipe-table row, split into cells, separators dropped.

    Header rows are kept so the caller can check the columns still mean what
    the parser assumes. The two-column decoration tables some READMEs open with
    are dropped by the cell-count floor.
    """
    rows = []
    for raw in markdown.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = line.strip("|").split("|")
        if len(cells) < 3:
            continue
        if set("".join(cells).strip()) <= {"-", ":", " "}:
            continue
        rows.append(cells)
    return rows


def is_header(cells: list[str]) -> bool:
    """A row whose first cell is the literal word Company."""
    return clean_cell(cells[0]).lower() == "company"


def table_rows(markdown: str) -> list[list[str]]:
    """Data rows only, for callers that do not care about the header."""
    return [cells for cells in all_rows(markdown) if not is_header(cells)]


USA_HEADING = re.compile(r"^#{1,4} [^\n]*\bUSA\b[^\n]*$", re.I | re.M)
FOREIGN_HEADING = re.compile(
    r"^#{1,4} [^\n]*(international|intl|non-us|worldwide)[^\n]*$", re.I | re.M
)


def usa_section(markdown: str) -> str:
    """Just the USA part of a README that also lists international roles.

    Anchored on the first heading that names USA *and* has a table under it:
    these READMEs open with a navigation heading ("USA Positions") that links
    down to the real one ("2027 USA SWE Internships"), and anchoring on the nav
    cut the body to nothing. Cut at the next heading naming international roles.

    An even earlier version anchored on the first "usa" substring anywhere and
    used a magic character offset, which any badge higher up would have shifted.
    """
    for start in USA_HEADING.finditer(markdown):
        body = markdown[start.start() :]
        stop = FOREIGN_HEADING.search(body, start.end() - start.start())
        section = body[: stop.start()] if stop else body
        if any(line.strip().startswith("|") for line in section.splitlines()):
            return section
    return markdown


# --- per-repo row parsers ---------------------------------------------------


EXPECTED_HEADERS = {
    "speedyapply": ("company", "position", "location"),
    "jobright": ("company", "job title", "location"),
    "zshah": ("company", "role", "apply", "location"),
    "resumax": ("company", "role", "location", "apply"),
}


def header_matches(cells: list[str], repo: Repo) -> bool:
    """Whether a header row still has the columns this parser expects.

    A silent column reorder would otherwise put the location text into the title
    and store garbage, rather than failing where it can be seen.
    """
    expected = EXPECTED_HEADERS.get(repo.kind, ())
    if not expected:
        return True
    labels = [clean_cell(cell).lower() for cell in cells]
    return all(any(name == label for label in labels) for name in expected)


def parse_json_listings(payload: list[dict]) -> list[dict]:
    """The shared schema of the four JSON repos.

    `active` false means the repo has closed the listing. `is_visible` false
    means it is hidden from their own README, so it is skipped too.
    """
    if not isinstance(payload, list):
        raise ValueError(f"expected a JSON array, got {type(payload).__name__}")

    found = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        if not item.get("active") or not item.get("is_visible"):
            continue
        places = item.get("locations") or []
        found.append(
            {
                "title": clean_cell(str(item.get("title") or "")),
                "company": clean_cell(str(item.get("company_name") or "")),
                "location": ", ".join(str(place) for place in places if place),
                "url": str(item.get("url") or "").strip(),
                "posted_at": _epoch_to_date(item.get("date_posted")),
            }
        )
    return found


AGE_IN_DAYS = re.compile(r"^(\d+)\+?\s*d$", re.I)
AGE_IN_MONTHS = re.compile(r"^(\d+)\s*mo$", re.I)
AGE_IN_WEEKS = re.compile(r"^(\d+)\s*w$", re.I)
AGE_IN_HOURS = re.compile(r"^(\d+)\s*h$", re.I)
DATE_WITH_YEAR = re.compile(r"^([A-Za-z]{3})[a-z]*\.?\s+(\d{1,2}),?\s+(\d{4})$")
DATE_NO_YEAR = re.compile(r"^([A-Za-z]{3})[a-z]*\.?\s+(\d{1,2})$")

MONTHS = {
    name: number
    for number, name in enumerate(
        ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"), 1
    )
}


def posted_date(cell: str, today: date | None = None) -> str:
    """The date a README row was posted, from its age or date column.

    Three formats appear across these repos and all three are handled: a
    relative age ("1d", "2mo"), a date with a year ("Oct 09, 2026"), and a date
    without one ("Oct 10"). Without this, 995 listings had no date at all and
    the "posted within" filter could not see them.

    A date with no year is read as the most recent one that is not in the
    future, so a December row read in January lands in the previous year.
    """
    text = clean_cell(cell)
    if not text:
        return ""
    now = today or datetime.now(UTC).date()

    hours = AGE_IN_HOURS.match(text)
    if hours:
        return now.isoformat()

    weeks = AGE_IN_WEEKS.match(text)
    if weeks:
        return (now - timedelta(weeks=int(weeks.group(1)))).isoformat()

    days = AGE_IN_DAYS.match(text)
    if days:
        return (now - timedelta(days=int(days.group(1)))).isoformat()

    months = AGE_IN_MONTHS.match(text)
    if months:
        return (now - timedelta(days=30 * int(months.group(1)))).isoformat()

    full = DATE_WITH_YEAR.match(text)
    if full:
        month = MONTHS.get(full.group(1).lower())
        if month:
            try:
                return date(int(full.group(3)), month, int(full.group(2))).isoformat()
            except ValueError:
                return ""

    partial = DATE_NO_YEAR.match(text)
    if partial:
        month = MONTHS.get(partial.group(1).lower())
        if month:
            for year in (now.year, now.year - 1):
                try:
                    guess = date(year, month, int(partial.group(2)))
                except ValueError:
                    continue
                # A day of slack: these repos write dates in their own
                # timezone, so "tomorrow" in UTC is a normal thing to see and
                # must not roll back a whole year.
                if guess <= now + timedelta(days=1):
                    return guess.isoformat()
    return ""


def _epoch_to_date(value: object) -> str:
    """`date_posted` is a unix timestamp in these repos."""
    try:
        return datetime.fromtimestamp(int(value), tz=UTC).date().isoformat()  # type: ignore[arg-type]
    except (TypeError, ValueError, OSError, OverflowError):
        return ""


def parse_speedyapply(cells: list[str]) -> dict | None:
    """| Company | Position | Location | [Salary] | Posting | Age |

    Salary is present in some tables and absent in others, so the apply link is
    found by scanning, not by index.
    """
    if len(cells) < 5:
        return None
    return {
        "title": clean_cell(cells[1]),
        "company": clean_cell(cells[0]),
        "location": clean_cell(cells[2]),
        "url": apply_link(cells),
        "posted_at": posted_date(cells[-1]),
    }


def parse_jobright(cells: list[str]) -> dict | None:
    """| Company | Job Title | Location | Work Model | Date Posted |"""
    if len(cells) < 5:
        return None
    return {
        "title": clean_cell(cells[1]),
        "company": clean_cell(cells[0]),
        "location": clean_cell(cells[2]),
        "url": apply_link(cells),
        "posted_at": posted_date(cells[-1]),
    }


def parse_zshah(cells: list[str]) -> dict | None:
    """| Company | Role | Apply | Location | Skills | Posted |"""
    if len(cells) < 6:
        return None
    return {
        "title": clean_cell(cells[1]),
        "company": clean_cell(cells[0]),
        "location": clean_cell(cells[3]),
        "url": apply_link(cells),
        "posted_at": posted_date(cells[-1]),
    }


def parse_resumax(cells: list[str]) -> dict | None:
    """| Company | Role | Location | Apply | Tailor | Age |

    The company cell links to resumax.ai rather than the employer, and the
    Tailor cell is a marketing link, so the apply URL is found by scanning from
    the second cell on — which lands on the real board link.
    """
    if len(cells) < 4:
        return None
    return {
        "title": clean_cell(cells[1]),
        "company": clean_cell(cells[0]),
        "location": clean_cell(cells[2]),
        "url": apply_link(cells),
        "posted_at": posted_date(cells[-1]),
    }


ROW_PARSERS = {
    "speedyapply": parse_speedyapply,
    "jobright": parse_jobright,
    "zshah": parse_zshah,
    "resumax": parse_resumax,
}


def parse_readme(markdown: str, repo: Repo) -> list[dict]:
    """Rows from a README, using that repo's column layout."""
    parse_row = ROW_PARSERS[repo.kind]
    body = usa_section(markdown) if repo.usa_only else markdown

    found = []
    saw_header = False
    for cells in all_rows(body):
        if is_header(cells):
            if not header_matches(cells, repo):
                raise ValueError(f"{repo.name}: table columns have changed")
            saw_header = True
            continue
        if is_closed("|".join(cells)):
            continue
        item = parse_row(cells)
        if item and item["title"] and item["company"]:
            found.append(item)

    if not saw_header:
        raise ValueError(f"{repo.name}: no recognizable table header")
    return found


# --- fetching ---------------------------------------------------------------


def dedupe_key(item: dict) -> tuple[str, str, str]:
    """Company plus title plus location, which is how repos overlap.

    The same opening appears in several repos under different apply links, so
    the url cannot be the key here.
    """
    return (
        item["company"].lower(),
        item["title"].lower(),
        item["location"].lower(),
    )


def to_listing(item: dict, repo_name: str) -> Listing:
    """A repo row as a normalized listing. Always `full_text=False`.

    The repos carry no description, so nothing from here can reach requirement
    extraction — that is what the flag is for.
    """
    return normalize(
        title=item["title"],
        company=item["company"],
        location=item["location"],
        url=item["url"],
        description="",
        posted_at=item.get("posted_at", ""),
        source=f"{SOURCE}:{repo_name.split('/')[0].lower()}",
        full_text=False,
    )


def fetch_github_repos(
    conn: sqlite3.Connection,
    roles: list[str],
    *,
    repos: tuple[Repo, ...] = REPOS,
) -> list[Listing]:
    """Listings from every tracked repo that match my roles, US and remote only.

    Each repo is one fetch. A JSON file is preferred where it exists; otherwise
    the README tables are parsed.

    The role filter is not optional. These repos list every discipline — product,
    HR, finance, hardware — so without it a run stores eight thousand rows and
    the board becomes unusable. Boards are still learned from the apply links of
    matching listings.
    """
    quota.check(conn, SOURCE)

    seen: dict[tuple[str, str, str], Listing] = {}
    with httpx.Client(timeout=90, follow_redirects=True) as http:
        for repo in repos:
            if not quota.may_call(conn, SOURCE, check_interval=False):
                break

            for item in _read_repo(conn, http, repo):
                if not item["url"] or not is_us_or_remote(item["location"]):
                    continue
                if not any(title_matches_role(item["title"], role) for role in roles):
                    continue

                key = dedupe_key(item)
                if key in seen:
                    continue

                listing = to_listing(item, repo.name)
                seen[key] = listing
                remember_board(conn, listing["url"], listing["company"])

    return list(seen.values())


def _read_repo(conn: sqlite3.Connection, http: httpx.Client, repo: Repo) -> list[dict]:
    """One repo's rows, from its JSON file when it has one, else its README."""
    path = JSON_PATH if repo.kind == "json" else README_PATH
    url = f"{RAW}/{repo.name}/{repo.branch}/{path}"

    try:
        response = http.get(url)
    except httpx.HTTPError as exc:
        db.record_api_call(conn, source=SOURCE, endpoint=url, ok=False, error=type(exc).__name__)
        return []

    db.record_api_call(
        conn,
        source=SOURCE,
        endpoint=url,
        status_code=response.status_code,
        ok=response.is_success,
    )
    if not response.is_success:
        return []

    try:
        if repo.kind == "json":
            return parse_json_listings(response.json())
        return parse_readme(response.text, repo)
    except (ValueError, KeyError, AttributeError, TypeError) as exc:
        db.record_api_call(
            conn, source=SOURCE, endpoint=url, ok=False, error=f"parse: {type(exc).__name__}"
        )
        return []
