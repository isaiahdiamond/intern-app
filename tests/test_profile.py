"""The profile is one row, replaced on edit, with industries kept in rank order."""

import pytest

from intern_app import profile

ANSWERS = {
    "school": "Example University",
    "major": "Applied Mathematics and Computer Science",
    "roles": [("Software Engineer Intern", "chip"), ("ML Infra Intern", "llm_suggested")],
    "industries": ["Finance & Trading", "Software & Internet"],
}


def test_saving_then_loading_round_trips(conn):
    profile.save_profile(conn, **ANSWERS)

    saved = profile.load_profile(conn)
    assert saved["school"] == "Example University"
    assert saved["roles"] == ["Software Engineer Intern", "ML Infra Intern"]
    assert saved["industries"] == ["Finance & Trading", "Software & Internet"]


def test_industry_order_is_the_preference_and_survives_a_reload(conn):
    """Rank is the whole signal, so the order chosen must come back unchanged."""
    profile.save_profile(conn, **{**ANSWERS, "industries": ["Gaming", "Consulting", "Education"]})

    assert profile.load_industry_ranking(conn) == ["Gaming", "Consulting", "Education"]
    ranks = conn.execute("SELECT industry, rank FROM profile_industries ORDER BY rank").fetchall()
    assert [row["rank"] for row in ranks] == [1, 2, 3]


def test_editing_replaces_rather_than_accumulating(conn):
    profile.save_profile(conn, **ANSWERS)
    profile.save_profile(
        conn,
        **{**ANSWERS, "school": "Other University", "roles": [("Data Science Intern", "chip")]},
    )

    assert conn.execute("SELECT COUNT(*) FROM profile").fetchone()[0] == 1
    saved = profile.load_profile(conn)
    assert saved["school"] == "Other University"
    assert saved["roles"] == ["Data Science Intern"]


def test_editing_keeps_the_original_created_at(conn):
    profile.save_profile(conn, **ANSWERS)
    conn.execute("UPDATE profile SET created_at = '2026-01-01T00:00:00+00:00'")

    profile.save_profile(conn, **{**ANSWERS, "school": "Other University"})

    saved = profile.load_profile(conn)
    assert saved["created_at"] == "2026-01-01T00:00:00+00:00"
    assert saved["updated_at"] > saved["created_at"]


def test_no_profile_yet_reads_as_not_onboarded(conn):
    assert profile.load_profile(conn) is None
    assert profile.is_onboarded(conn) is False


def test_a_profile_with_no_roles_does_not_count_as_onboarded(conn):
    """It cannot drive a fetch, so onboarding is not finished."""
    profile.save_profile(conn, **{**ANSWERS, "roles": []})

    assert profile.is_onboarded(conn) is False


def test_an_unknown_role_source_is_refused(conn):
    with pytest.raises(ValueError, match="role source must be one of"):
        profile.save_profile(conn, **{**ANSWERS, "roles": [("X Intern", "guessed")]})


def test_duplicate_roles_and_industries_are_deduped(conn):
    """The columns are UNIQUE, so a repeated value used to be a 500."""
    profile.save_profile(
        conn,
        school="Example U",
        major="Applied Math & CS",
        roles=[("Software Engineer Intern", "chip"), ("Software Engineer Intern", "chip")],
        industries=["Gaming", "Gaming", "Consulting"],
    )

    saved = profile.load_profile(conn)
    assert saved["roles"] == ["Software Engineer Intern"]
    assert saved["industries"] == ["Gaming", "Consulting"]


def test_a_failed_save_does_not_destroy_the_previous_answers(conn):
    """Regression: `with conn:` is a no-op under isolation_level=None, so a
    failure after the DELETE left the profile with no roles at all."""
    profile.save_profile(conn, **ANSWERS)

    with pytest.raises(ValueError):
        profile.save_profile(
            conn,
            school="Example U",
            major="Applied Math & CS",
            roles=[("Data Science Intern", "not_a_valid_source")],
            industries=["Gaming"],
        )

    # The original answers must still be intact.
    saved = profile.load_profile(conn)
    assert saved["roles"] == ["Software Engineer Intern", "ML Infra Intern"]
    assert saved["industries"] == ["Finance & Trading", "Software & Internet"]


def test_a_degree_opens_everything_at_or_below_it():
    """A master's student can take a bachelor's posting. A bachelor's student
    cannot take a PhD one."""
    assert profile.degrees_open_to("masters") == ["any", "undergrad", "masters"]
    assert profile.degrees_open_to("undergrad") == ["any", "undergrad"]
    assert profile.degrees_open_to("phd") == ["any", "undergrad", "masters", "phd"]


def test_no_degree_set_means_no_filter_rather_than_no_results():
    assert profile.degrees_open_to("") == []


def test_what_the_search_is_for_is_saved_and_read_back(conn):
    profile.save_profile(
        conn,
        school="Example U",
        major="CS",
        roles=[("Software Engineer Intern", "chip")],
        industries=[],
        education="masters",
        seeking=["new_grad", "intern"],
    )

    saved = profile.load_profile(conn)

    assert saved["education"] == "masters"
    # Listed in the app's own order, not the order they were ticked in.
    assert saved["seeking"] == ["intern", "new_grad"]


def test_a_level_nobody_searches_for_is_dropped(conn):
    """`other` is an experienced hire. It is a reading of a listing, never
    something the profile asks for."""
    profile.save_profile(
        conn,
        school="Example U",
        major="CS",
        roles=[("Software Engineer Intern", "chip")],
        industries=[],
        seeking=["intern", "other"],
    )

    assert profile.load_profile(conn)["seeking"] == ["intern"]
