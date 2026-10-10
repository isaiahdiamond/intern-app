"""The role chips offered per major, and the industries offered for ranking.

The lists are hardcoded on purpose: the scope right now is tech majors and one
user, and a static list beats a crosswalk lookup until that changes.

Each major's roles are in the order they are shown — most common internship
first, because that ordering is what makes the chips quick to answer. The role
wording is how postings are actually written ("Software Engineer Intern"), not
how the census names occupations ("Software Developers"), since these strings
become search queries in phase 2.

Scope for each major came from the NCES CIP-SOC crosswalk, minus the
postsecondary-teaching occupations and the manager and catch-all codes that no
intern holds.
"""

from __future__ import annotations

# Keyed by a lowercase, punctuation-free form of what the user typed.
ROLES_BY_MAJOR: dict[str, tuple[str, ...]] = {
    "applied mathematics and computer science": (
        "Software Engineer Intern",
        "Data Science Intern",
        "Machine Learning Intern",
        "Data Analyst Intern",
        "Backend Engineer Intern",
        "Quantitative Research Intern",
        "Data Engineer Intern",
        "Research Intern",
        "Full Stack Engineer Intern",
        "Quantitative Trading Intern",
        "Actuarial Intern",
        "Statistician Intern",
        "Computer Scientist Intern",
        "Operations Research Intern",
        "Mathematician Intern",
        "Mechanical Engineer Intern",
        "Electrical Engineer Intern",
    ),
    "computer science": (
        "Software Engineer Intern",
        "Backend Engineer Intern",
        "Full Stack Engineer Intern",
        "Frontend Engineer Intern",
        "Machine Learning Intern",
        "Data Science Intern",
        "Site Reliability Engineer Intern",
        "Security Engineer Intern",
        "Mobile Engineer Intern",
        "QA Engineer Intern",
        "Data Engineer Intern",
        "Research Intern",
    ),
    "applied mathematics": (
        "Data Science Intern",
        "Data Analyst Intern",
        "Quantitative Research Intern",
        "Machine Learning Intern",
        "Actuarial Intern",
        "Quantitative Trading Intern",
        "Statistician Intern",
        "Operations Research Intern",
        "Mathematician Intern",
        "Research Intern",
        "Data Engineer Intern",
    ),
    "mathematics": (
        "Data Analyst Intern",
        "Data Science Intern",
        "Actuarial Intern",
        "Quantitative Research Intern",
        "Statistician Intern",
        "Machine Learning Intern",
        "Research Intern",
    ),
    "data science": (
        "Data Science Intern",
        "Data Analyst Intern",
        "Machine Learning Intern",
        "Data Engineer Intern",
        "Business Intelligence Intern",
        "Research Intern",
        "Software Engineer Intern",
    ),
    "computer engineering": (
        "Software Engineer Intern",
        "Embedded Software Intern",
        "Hardware Engineer Intern",
        "Firmware Engineer Intern",
        "Backend Engineer Intern",
        "FPGA Engineer Intern",
        "Site Reliability Engineer Intern",
    ),
    "information systems": (
        "Software Engineer Intern",
        "Data Analyst Intern",
        "IT Intern",
        "Business Analyst Intern",
        "Security Analyst Intern",
        "Database Administrator Intern",
        "Business Intelligence Intern",
    ),
    "electrical engineering": (
        "Hardware Engineer Intern",
        "Embedded Software Intern",
        "Firmware Engineer Intern",
        "Software Engineer Intern",
        "Signal Processing Intern",
        "FPGA Engineer Intern",
    ),
}

# Shown for ranking. Tech-weighted, since that is the current scope.
INDUSTRIES: tuple[str, ...] = (
    "Software & Internet",
    "Finance & Trading",
    "Healthcare & Biotech",
    "Aerospace & Defense",
    "Consulting",
    "Gaming",
    "E-commerce & Retail",
    "Education",
    "Energy & Climate",
    "Government & Public Sector",
    "Media & Entertainment",
    "Transportation & Logistics",
    "Hardware & Semiconductors",
    "Telecommunications",
    "Non-profit",
)

# Offered when a major matches nothing known, so the form is never empty.
FALLBACK_ROLES: tuple[str, ...] = (
    "Software Engineer Intern",
    "Data Science Intern",
    "Data Analyst Intern",
    "Machine Learning Intern",
    "Research Intern",
    "Business Analyst Intern",
)


def normalize_major(major: str) -> str:
    """Reduce a typed major to the key used in ROLES_BY_MAJOR.

    Lowercased, punctuation dropped, "and" and "&" treated as the same word, so
    "Applied Math & CS" and "applied mathematics and computer science" can reach
    the same entry.
    """
    text = major.lower().replace("&", " and ")
    text = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in text)
    words = []
    for word in text.split():
        if word in {"math", "maths"}:
            word = "mathematics"
        elif word in {"cs", "compsci"}:
            words.extend(["computer", "science"])
            continue
        words.append(word)
    return " ".join(words)


def roles_for_major(major: str) -> tuple[str, ...]:
    """The chips to show for a major, most common internship first.

    Falls back to a general tech list rather than returning nothing, because an
    empty chip list would strand the user on question 3 with only the Other
    button.
    """
    key = normalize_major(major)
    if key in ROLES_BY_MAJOR:
        return ROLES_BY_MAJOR[key]

    # A combined major such as "applied mathematics and computer science" that
    # is not listed verbatim: merge the halves it does contain, keeping the
    # order of the first match so the most common roles stay at the front.
    merged: list[str] = []
    for known, roles in ROLES_BY_MAJOR.items():
        if known in key:
            for role in roles:
                if role not in merged:
                    merged.append(role)
    return tuple(merged) if merged else FALLBACK_ROLES
