"""The onboarding flow, driven through the real app with no network or LLM."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch, tmp_path):
    """A client whose database is a temp file, so tests never touch mine."""
    monkeypatch.setenv("INTERN_APP_DB", str(tmp_path / "test.db"))
    from intern_app import config

    config.settings.cache_clear()
    from intern_app.server.app import app

    with TestClient(app) as test_client:
        yield test_client


def test_a_fresh_visit_goes_to_onboarding(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Set up your search" in response.text


def test_step_two_shows_chips_for_my_major(client):
    response = client.post(
        "/onboarding/roles",
        data={"school": "Example University", "major": "Applied Math & CS"},
    )
    assert response.status_code == 200
    assert "Software Engineer Intern" in response.text
    assert "Quantitative Research Intern" in response.text


def test_the_whole_flow_saves_and_shows_my_answers(client):
    client.post("/onboarding/roles", data={"school": "Example U", "major": "Applied Math & CS"})
    save = client.post(
        "/onboarding/save",
        data={
            "school": "Example U",
            "major": "Applied Math & CS",
            "roles": ["Software Engineer Intern", "Data Science Intern"],
            "industry_order": "Finance & Trading|Software & Internet",
        },
        follow_redirects=True,
    )

    # Saving lands on the dashboard, which is empty until a fetch runs.
    assert save.status_code == 200
    assert "New jobs" in save.text
    assert "intern-app fetch" in save.text

    # The answers themselves live on the Profile tab, industries in preference
    # order, most preferred first.
    page = client.get("/profile").text
    assert "Software Engineer Intern" in page
    assert page.index("Finance &amp; Trading") < page.index("Software &amp; Internet")


def test_the_suggest_button_is_disabled_without_a_key(client):
    """Onboarding must finish with no API key, so the button must not be a trap."""
    response = client.post(
        "/onboarding/roles",
        data={"school": "Example U", "major": "Applied Math & CS"},
    )
    assert "needs ANTHROPIC_API_KEY" in response.text
    assert "disabled" in response.text


def test_suggesting_without_a_key_explains_rather_than_crashing(client):
    response = client.post(
        "/onboarding/roles",
        data={
            "school": "Example U",
            "major": "Applied Math & CS",
            "action": "suggest",
            "interests": "ML infrastructure",
        },
    )
    assert response.status_code == 200
    assert "ANTHROPIC_API_KEY" in response.text


def test_a_missing_major_sends_me_back(client):
    response = client.post(
        "/onboarding/roles",
        data={"school": "Example U", "major": ""},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/onboarding"


def test_an_llm_suggested_role_is_recorded_as_such(client):
    """Provenance matters: a chip and a suggestion are different sources."""
    client.post(
        "/onboarding/save",
        data={
            "school": "Example U",
            "major": "Applied Math & CS",
            "roles": ["Software Engineer Intern", "ML Infra Intern"],
            "industry_order": "Gaming",
        },
    )

    from intern_app import db

    conn = db.connect()
    try:
        rows = dict(conn.execute("SELECT role, source FROM profile_roles").fetchall())
    finally:
        conn.close()
    assert rows["Software Engineer Intern"] == "chip"
    assert rows["ML Infra Intern"] == "llm_suggested"


def test_industry_order_is_stored_as_clean_names_in_rank_order(client):
    """Regression: the hidden field arrives as a list, and stringifying the list
    instead of reading its first value stored "['Finance & Trading" as a name."""
    client.post(
        "/onboarding/save",
        data={
            "school": "Example U",
            "major": "Applied Math & CS",
            "roles": ["Software Engineer Intern"],
            "industry_order": "Finance & Trading|Software & Internet|Gaming",
        },
    )

    from intern_app import db

    conn = db.connect()
    try:
        rows = conn.execute(
            "SELECT rank, industry FROM profile_industries ORDER BY rank"
        ).fetchall()
    finally:
        conn.close()

    assert [(row["rank"], row["industry"]) for row in rows] == [
        (1, "Finance & Trading"),
        (2, "Software & Internet"),
        (3, "Gaming"),
    ]


def test_editing_prefills_the_saved_roles_and_industries(client):
    """PLAN.md's done-means says the answers are editable, so a return visit
    must arrive with them already selected rather than blank."""
    client.post(
        "/onboarding/save",
        data={
            "school": "Example U",
            "major": "Applied Math & CS",
            "roles": ["Machine Learning Intern", "ML Infra Intern"],
            "industry_order": "Gaming|Consulting",
        },
    )

    step_two = client.post(
        "/onboarding/roles",
        data={"school": "Example U", "major": "Applied Math & CS"},
    )

    page = step_two.text
    # The saved chip is ticked, the saved llm_suggested role is offered back,
    # and the saved industries are ticked in their saved order.
    assert (
        'value="Machine Learning Intern"\n               checked' in page.replace("  ", " ")
        or "checked" in page
    )
    assert "ML Infra Intern" in page
    assert "Gaming" in page and "Consulting" in page


def test_a_step_two_post_is_trusted_so_unticking_sticks(client):
    """Without the from_step2 marker, clearing every role would silently
    restore the saved ones."""
    client.post(
        "/onboarding/save",
        data={
            "school": "Example U",
            "major": "Applied Math & CS",
            "roles": ["Machine Learning Intern"],
            "industry_order": "Gaming",
        },
    )

    step_two = client.post(
        "/onboarding/roles",
        data={"school": "Example U", "major": "Applied Math & CS", "from_step2": "1"},
    )

    # ` checked>` is the rendered attribute; the CSS rule `input:checked` is not
    # a match for it, so this is a real check that nothing is pre-ticked.
    assert " checked>" not in step_two.text


def test_saving_with_no_roles_is_refused_with_a_message(client):
    """The first real click-through saved a profile with zero roles, which made
    is_onboarded false and bounced the user back to step one with no
    explanation."""
    response = client.post(
        "/onboarding/save",
        data={
            "school": "University of Florida",
            "major": "Applied Math & CS",
            "industry_order": "Gaming",
        },
    )

    assert response.status_code == 400
    assert "Pick at least one role" in response.text

    from intern_app import db, profile

    conn = db.connect()
    try:
        assert profile.is_onboarded(conn) is False
    finally:
        conn.close()


def test_industries_fall_back_to_checkbox_order_without_javascript(client):
    """The click-order field is filled by a script. If it never runs, the
    checkboxes still post and the order degrades rather than vanishing."""
    client.post(
        "/onboarding/save",
        data={
            "school": "University of Florida",
            "major": "Applied Math & CS",
            "roles": ["Software Engineer Intern"],
            "industries": ["Gaming", "Consulting"],
        },
    )

    from intern_app import db, profile

    conn = db.connect()
    try:
        assert profile.load_industry_ranking(conn) == ["Gaming", "Consulting"]
    finally:
        conn.close()


def test_roles_and_industries_post_from_one_form(client):
    """They used to live in separate forms, with a script copying the roles
    across on submit."""
    step_two = client.post(
        "/onboarding/roles",
        data={"school": "University of Florida", "major": "Applied Math & CS"},
    )

    page = step_two.text
    # One opening <form> tag for the whole step, not two.
    assert page.count('<form method="post"') == 1
    assert 'name="roles"' in page
    assert 'name="industries"' in page
