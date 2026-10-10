"""Deciding whether a posting title is really for one of my roles.

Shared by every source that returns more than it was asked for: a Muse category
holds 874 internships, and a community repo lists every discipline. Without this
the board fills with roles nobody searched for.
"""

from __future__ import annotations

# Words that say nothing about which role a posting is for. The level filter
# already guarantees seniority, so these only get in the way of matching.
FILLER = frozenset(
    {
        "intern",
        "interns",
        "internship",
        "internships",
        "co",
        "op",
        "coop",
        "new",
        "grad",
        "graduate",
        "entry",
        "level",
        "summer",
        "fall",
        "winter",
        "spring",
        "the",
        "and",
        "of",
        "a",
        "an",
        "for",
        "to",
        "in",
        "at",
        "program",
        "university",
        "student",
        "early",
        "career",
        "i",
        "ii",
    }
)

STEM_LENGTH = 5

# Different words for the same job. Applied to roles and titles alike before
# stemming, because stems alone cannot bridge "Back-End" and "backend" or know
# that a Software Developer and a Software Engineer are the same opening.
ALIASES: tuple[tuple[str, str], ...] = (
    ("back end", "backend"),
    ("front end", "frontend"),
    ("full stack", "fullstack"),
    ("cyber security", "security"),
    ("cybersecurity", "security"),
    ("swe", "software engineer"),
    ("sde", "software engineer"),
    ("ml", "machine learning"),
    ("ai", "machine learning"),
    # Spelled out as well as abbreviated: "Artificial Intelligence Co-Op/Intern"
    # matched no role at all until this was added.
    ("artificial intelligence", "machine learning"),
    ("deep learning", "machine learning"),
    ("developer", "engineer"),
    ("programmer", "engineer"),
    ("quant", "quantitative"),
)


def normalized_words(text: str) -> list[str]:
    """Lowercase alphanumeric words, with the aliases above applied."""
    cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
    cleaned = f" {' '.join(cleaned.split())} "
    for term, replacement in ALIASES:
        cleaned = cleaned.replace(f" {term} ", f" {replacement} ")
    return cleaned.split()


def stems(text: str) -> set[str]:
    """Meaningful words from a title, cut to a crude stem.

    Truncating to five characters is what makes "Data Scientist" match a role
    written "Data Science", and "Software Engineering" match "Software
    Engineer" — the suffixes differ but the stems do not.
    """
    return {
        word[:STEM_LENGTH]
        for word in normalized_words(text)
        if word not in FILLER and len(word) > 1
    }


def phrase_in(phrase: str, words: list[str]) -> bool:
    """Whether every word of `phrase` appears in order inside `words`."""
    needle = phrase.split()
    for start in range(len(words) - len(needle) + 1):
        if words[start : start + len(needle)] == needle:
            return True
    return False


def title_matches_role(title: str, role: str) -> bool:
    """Whether a returned posting is really for this role.

    A Muse category is broad — "Software Engineering" covers 874 internships —
    so the role has to be matched against the title here.

    Two stems in common is the bar. A role with only one meaningful word, like
    "Actuarial Intern", instead needs that whole word in the title: matching it
    on a stem let "Product" match "Production Engineer" and "Research" match
    anything with the word in it.
    """
    role_words = [word for word in normalized_words(role) if word not in FILLER]
    if not role_words:
        return False

    title_words = normalized_words(title)
    if phrase_in(" ".join(role_words), title_words):
        return True

    if len(set(role_words)) == 1:
        return role_words[0] in title_words

    return len(stems(role) & stems(title)) >= 2
