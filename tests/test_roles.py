"""Chip lists must be sensible for a real major, and never empty."""

from intern_app.roles import FALLBACK_ROLES, INDUSTRIES, normalize_major, roles_for_major


def test_my_major_matches_however_i_type_it():
    """Applied Math & CS and its long form must reach the same chip list."""
    assert normalize_major("CS") == "computer science"
    assert normalize_major("Applied Math") == "applied mathematics"

    long_form = roles_for_major("Applied Mathematics and Computer Science")
    assert roles_for_major("Applied Math & CS") == long_form
    assert roles_for_major("applied mathematics and computer science") == long_form
    assert long_form[0] == "Software Engineer Intern"


def test_a_known_major_leads_with_its_most_common_role():
    assert roles_for_major("Computer Science")[0] == "Software Engineer Intern"
    assert roles_for_major("Applied Mathematics")[0] == "Data Science Intern"


def test_an_unknown_major_still_gets_chips():
    """An empty chip list would strand the user on question 3."""
    assert roles_for_major("Underwater Basket Weaving") == FALLBACK_ROLES


def test_a_combined_major_merges_the_halves_it_knows():
    merged = roles_for_major("Mathematics and Data Science")
    assert "Data Analyst Intern" in merged
    assert len(merged) > len(roles_for_major("Mathematics"))


def test_every_role_reads_as_an_intern_posting_title():
    """These strings become search queries in phase 2, so they must look real."""
    from intern_app.roles import ROLES_BY_MAJOR

    for major, titles in ROLES_BY_MAJOR.items():
        assert len(titles) == len(set(titles)), f"{major} has a duplicate chip"
        for title in titles:
            assert title.endswith("Intern"), f"{title!r} in {major} is not an intern title"
            assert title == title.strip()


def test_industries_are_unique():
    """Duplicates would collide with the UNIQUE constraint on rank insert."""
    assert len(INDUSTRIES) == len(set(INDUSTRIES))
