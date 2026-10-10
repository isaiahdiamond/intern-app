"""The listing shape every source returns, and the one function that builds it.

A source parses its own API's response and hands each record to `normalize`. No
source assembles the dict itself — that keeps the shape in one place, so a change
to the contract is a change to this file.
"""

from __future__ import annotations

import html
import re
from typing import Any, TypedDict

# Every key is required and every source produces all of them.
LISTING_FIELDS = (
    "title",
    "company",
    "location",
    "url",
    "description",
    "posted_at",
    "source",
    "full_text",
)


class Listing(TypedDict):
    title: str
    company: str
    location: str
    url: str
    description: str
    posted_at: str
    source: str
    full_text: bool


_TAG = re.compile(r"<[^>]+>")
_WHITESPACE = re.compile(r"[ \t\r\f\v]+")
_BLANK_LINES = re.compile(r"\n{3,}")


def strip_html(value: str) -> str:
    """Turn an HTML job description into readable plain text.

    Several boards return descriptions as HTML. Block-level tags become newlines
    so paragraph and list structure survives, which matters because the extractor
    reads this text.
    """
    if not value:
        return ""
    text = re.sub(r"(?i)<\s*br\s*/?\s*>", "\n", value)
    # `<li>` already opens its own line below, so closing it must not add a second.
    text = re.sub(r"(?i)</\s*(p|div|tr|h[1-6])\s*>", "\n", text)
    text = re.sub(r"(?i)<\s*li[^>]*>", "\n- ", text)
    text = _TAG.sub("", text)
    text = html.unescape(text)
    text = _WHITESPACE.sub(" ", text)
    text = "\n".join(line.strip() for line in text.split("\n"))
    return _BLANK_LINES.sub("\n\n", text).strip()


def clean(value: Any) -> str:
    """Coerce any API field to a trimmed string. `None` and missing become ""."""
    if value is None:
        return ""
    return _WHITESPACE.sub(" ", str(value)).strip()


def normalize(
    *,
    title: Any,
    company: Any,
    location: Any,
    url: Any,
    description: Any,
    posted_at: Any,
    source: str,
    full_text: bool,
    is_html: bool = False,
) -> Listing:
    """Build a `Listing`, enforcing the contract in `CLAUDE.md`.

    `full_text` is the extractor's gate: pass `True` only when `description` is
    the complete posting. A truncated or absent description is `False`, and its
    description is dropped so no partial text can reach skill extraction.
    """
    if not isinstance(full_text, bool):
        raise TypeError(f"full_text must be a bool, got {type(full_text).__name__}")

    body = clean(description) if not is_html else strip_html(str(description or ""))
    if not full_text:
        body = ""

    listing: Listing = {
        "title": clean(title),
        "company": clean(company),
        "location": clean(location),
        "url": clean(url),
        "description": body,
        "posted_at": clean(posted_at),
        "source": source,
        "full_text": full_text,
    }

    if full_text and not listing["description"]:
        raise ValueError(
            f"{source}: full_text=True but the description is empty ({listing['url']})"
        )
    if not listing["url"]:
        raise ValueError(f"{source}: a listing has no url, which is what we dedupe on")
    return listing
