"""LinkedIn job alerts, read from my own Yahoo inbox over IMAP.

This is not scraping. LinkedIn emails these alerts to me because I asked it to;
reading my own mail is the one sanctioned way to get LinkedIn listings, and the
project forbids touching their site.

Four decisions worth knowing:

The **plain-text** part of each alert is parsed, not the HTML. Each alert is
81 KB of HTML but 10 KB of text laid out as repeating
`Title / Company / City, ST / View job: <url>` blocks, which is far less likely
to break when LinkedIn restyles the email.

The mailbox is opened **read-only** and only the LinkedIn job-alert sender is
searched, so no other mail is ever fetched. No message body is stored.

Apply URLs are **canonicalised to the job id**. The links in the mail carry
`otpToken` and `midToken` query parameters that identify my email account;
storing them would put personal tokens in the database and in any export.

Role filtering is deliberately **not** applied. I set these alerts up myself, so
every one of them is already something I asked to be told about.
"""

from __future__ import annotations

import contextlib
import email
import imaplib
import re
import sqlite3
from email.header import decode_header
from email.message import Message

from intern_app import db
from intern_app.config import settings
from intern_app.sources import quota
from intern_app.sources.base import Listing, normalize
from intern_app.sources.us_filter import is_us_or_remote

SOURCE = "linkedin_mail"

# The sender LinkedIn uses for job alert digests. Other LinkedIn mail — profile
# views, invitations, messages — is never fetched.
ALERT_SENDER = "jobalerts-noreply@linkedin.com"

IMAP_PORT = 993

# Blocks inside the text part are separated by a run of dashes.
BLOCK_SEPARATOR = re.compile(r"\n-{10,}\n")

JOB_URL = re.compile(r"https://www\.linkedin\.com/comm/jobs/view/(\d+)")
VIEW_JOB_LINE = re.compile(r"^View job:\s*(\S+)", re.M)

# Lines that are chrome rather than job detail.
NOISE = (
    "this company is actively hiring",
    "see all jobs",
    "view job",
    "unsubscribe",
    "actively reviewing applicants",
    "be an early applicant",
    "your job alert for",
    "easy apply",
    "promoted",
)


def canonical_url(job_id: str) -> str:
    """The public URL for a job id, with every tracking parameter dropped.

    The mail links carry tokens tied to my email account, so only the id is
    kept and the clean public address is rebuilt from it.
    """
    return f"https://www.linkedin.com/jobs/view/{job_id}/"


def decode_field(value: str | None) -> str:
    """A header value as readable text, whatever encoding it arrived in."""
    parts = []
    for chunk, charset in decode_header(value or ""):
        if isinstance(chunk, bytes):
            parts.append(chunk.decode(charset or "utf-8", "replace"))
        else:
            parts.append(chunk)
    return " ".join("".join(parts).split())


def text_part(message: Message) -> str:
    """The plain-text body of a multipart alert."""
    for part in message.walk():
        if part.get_content_type() == "text/plain":
            payload = part.get_payload(decode=True) or b""
            return payload.decode(part.get_content_charset() or "utf-8", "replace")
    return ""


def parse_alert(text: str) -> list[dict]:
    """Jobs from one alert email's text body.

    Each block holds the title, the company and the location on their own lines
    before the `View job:` link, so the lines are read in order and the chrome
    lines are skipped.
    """
    jobs: list[dict] = []
    for block in BLOCK_SEPARATOR.split(text):
        link = VIEW_JOB_LINE.search(block)
        if not link:
            continue
        found = JOB_URL.search(link.group(1))
        if not found:
            continue

        lines = []
        for raw in block.splitlines():
            line = raw.strip()
            if not line or line.startswith("View job:"):
                continue
            if any(noise in line.lower() for noise in NOISE):
                continue
            lines.append(line)

        if len(lines) < 2:
            continue
        jobs.append(
            {
                "title": lines[0],
                "company": lines[1],
                "location": lines[2] if len(lines) > 2 else "",
                "url": canonical_url(found.group(1)),
            }
        )
    return jobs


def to_listing(job: dict) -> Listing:
    """One alerted job as a normalized listing.

    `full_text` is False: the alert carries no description, and the posting
    itself must not be fetched.
    """
    return normalize(
        title=job["title"],
        company=job["company"],
        location=job["location"],
        url=job["url"],
        description="",
        posted_at="",
        source=SOURCE,
        full_text=False,
    )


def fetch_linkedin_mail(conn: sqlite3.Connection, *, limit: int = 60) -> list[Listing]:
    """Jobs from the most recent LinkedIn job-alert emails in my inbox.

    `limit` caps how many messages are read, newest first. The same job appears
    across many alerts, so results are deduped on the canonical url.
    """
    cfg = settings()
    host = cfg.get("YAHOO_IMAP_HOST", "imap.mail.yahoo.com")
    user = cfg.require("YAHOO_EMAIL")
    password = cfg.require("YAHOO_APP_PASSWORD")

    quota.check(conn, SOURCE)
    found: dict[str, Listing] = {}

    mailbox = imaplib.IMAP4_SSL(host, IMAP_PORT)
    try:
        mailbox.login(user, password)
        # Read-only: nothing in the mailbox can be modified or deleted.
        mailbox.select("INBOX", readonly=True)
        db.record_api_call(conn, source=SOURCE, endpoint=f"imaps://{host}/INBOX", ok=True)

        status, data = mailbox.search(None, f'(FROM "{ALERT_SENDER}")')
        if status != "OK":
            return []
        message_ids = (data[0] or b"").split()

        for message_id in reversed(message_ids[-limit:]):
            status, raw = mailbox.fetch(message_id, "(BODY.PEEK[])")
            if status != "OK" or not raw or not raw[0]:
                continue
            message = email.message_from_bytes(raw[0][1])
            for job in parse_alert(text_part(message)):
                if not is_us_or_remote(job["location"]):
                    continue
                listing = to_listing(job)
                found.setdefault(listing["url"], listing)
    except (imaplib.IMAP4.error, OSError) as exc:
        # The password is never included: only the exception class.
        db.record_api_call(
            conn,
            source=SOURCE,
            endpoint=f"imaps://{host}/INBOX",
            ok=False,
            error=type(exc).__name__,
        )
        raise
    finally:
        # A failed logout does not matter; the session closes either way.
        with contextlib.suppress(imaplib.IMAP4.error, OSError):
            mailbox.logout()

    return list(found.values())
