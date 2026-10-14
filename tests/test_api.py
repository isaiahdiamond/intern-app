"""The JSON endpoints the React frontend reads.

These exist so the frontend is never wired to mock data by accident: every
field the UI renders has to come back from a real query here.
"""

import pytest
from fastapi.testclient import TestClient

from intern_app import db, profile
from intern_app.sources.base import normalize


@pytest.fixture
def client(monkeypatch, tmp_path):
    """A client whose database is a temp file, seeded with three listings."""
    path = tmp_path / "test.db"
    monkeypatch.setenv("INTERN_APP_DB", str(path))
    from intern_app import config

    config.settings.cache_clear()

    conn = db.connect(path)
    db.upsert_listings(
        conn,
        [
            normalize(
                title="Software Engineer Intern - Summer 2027",
                company="TikTok",
                location="Seattle, WA",
                url="https://example.com/a",
                description="Python.",
                posted_at="2026-10-01",
                source="muse",
                full_text=True,
            ),
            normalize(
                title="Quant Intern",
                company="TD Bank",
                location="New York, NY",
                url="https://example.com/b",
                description="",
                posted_at="2026-10-02",
                source="adzuna",
                full_text=False,
            ),
        ],
    )
    db.set_company_industry(conn, "TikTok", "Software & Internet")
    db.set_company_industry(conn, "TD Bank", "Finance & Trading")
    db.set_listing_detail(
        conn,
        listing_id=conn.execute("SELECT id FROM listings WHERE company = 'TikTok'").fetchone()[
            "id"
        ],
        clean_title="Software Engineer",
        level="intern",
        education="undergrad",
        term="Summer 2027",
    )
    profile.save_profile(
        conn,
        school="Example U",
        major="Applied Math & CS",
        roles=[("Software Engineer Intern", "chip")],
        industries=["Finance & Trading", "Software & Internet"],
    )
    conn.close()

    from intern_app.server.app import app

    with TestClient(app) as test_client:
        yield test_client


def test_listings_come_back_with_the_fields_the_board_renders(client):
    body = client.get("/api/listings").json()

    assert body["total"] == 2
    row = next(r for r in body["listings"] if r["company"] == "TikTok")
    assert row["display_title"] == "Software Engineer"
    assert row["title"] == "Software Engineer Intern - Summer 2027"
    assert row["level"] == "intern"
    assert row["education"] == "undergrad"
    assert row["industry"] == "Software & Internet"
    assert row["has_icon"] == 0
    assert row["status"] == "new"


def test_the_industry_ranking_orders_the_page(client):
    body = client.get("/api/listings").json()

    assert [row["company"] for row in body["listings"]] == ["TD Bank", "TikTok"]


def test_a_level_filter_narrows_the_page_and_its_total(client):
    body = client.get("/api/listings", params={"level": "intern"}).json()

    assert body["total"] == 1
    assert body["listings"][0]["company"] == "TikTok"


def test_setting_a_status_moves_a_listing_to_the_tracker(client):
    listing_id = client.get("/api/listings").json()["listings"][0]["id"]

    posted = client.post("/api/status", json={"listing_id": listing_id, "status": "applied"})

    assert posted.status_code == 200
    assert posted.json()["counts"]["applied"] == 1
    tracked = client.get("/api/tracker").json()["listings"]
    assert [row["id"] for row in tracked] == [listing_id]
    assert [entry["status"] for entry in tracked[0]["history"]] == ["applied"]


def test_an_unknown_status_is_refused_rather_than_stored(client):
    listing_id = client.get("/api/listings").json()["listings"][0]["id"]

    refused = client.post("/api/status", json={"listing_id": listing_id, "status": "ghosted"})

    assert refused.status_code == 400
    assert client.get("/api/tracker").json()["listings"] == []


def test_search_reaches_listings_the_dashboard_has_dropped(client):
    listing_id = client.get("/api/listings").json()["listings"][0]["id"]
    client.post("/api/status", json={"listing_id": listing_id, "status": "rejected"})

    assert client.get("/api/search").json()["total"] == 2
    assert client.get("/api/search", params={"q": "TikTok"}).json()["total"] == 1


def test_filters_carry_everything_the_sidebar_needs(client):
    body = client.get("/api/filters").json()

    assert body["industries"] == ["Finance & Trading", "Software & Internet"]
    assert body["roles"] == ["Software Engineer Intern"]
    assert body["level_counts"] == {"": 1, "intern": 1}
    assert body["status_counts"]["new"] == 2


def test_the_profile_endpoint_says_onboarding_is_done(client):
    body = client.get("/api/profile").json()

    assert body["onboarded"] is True
    assert body["profile"]["school"] == "Example U"


def test_a_manual_job_posts_straight_into_the_tracker(client):
    added = client.post(
        "/api/manual",
        json={"title": "Research Intern", "company": "Acme", "status": "applied"},
    )

    assert added.status_code == 200
    tracked = client.get("/api/tracker").json()["listings"]
    assert [row["company"] for row in tracked] == ["Acme"]
    assert tracked[0]["source"] == "manual"


def test_a_manual_job_without_a_company_is_refused(client):
    refused = client.post("/api/manual", json={"title": "Research Intern", "company": ""})

    assert refused.status_code == 400
    assert client.get("/api/tracker").json()["listings"] == []


def test_an_icon_is_served_from_our_own_origin(client):
    from intern_app import db, icons

    conn = db.connect()
    icons.save_icon(
        conn,
        company="TikTok",
        domain="lifeattiktok.com",
        domain_from="url",
        image=b"\x89PNG\r\n",
        content_type="image/png",
        ok=True,
    )
    conn.close()

    served = client.get("/api/icon/TikTok")

    assert served.status_code == 200
    assert served.content == b"\x89PNG\r\n"
    assert served.headers["content-type"] == "image/png"


def test_a_company_with_no_icon_404s_so_the_row_draws_its_tile(client):
    assert client.get("/api/icon/Nobody%20Inc").status_code == 404


def test_the_degree_filter_narrows_the_page_and_its_total(client):
    body = client.get("/api/listings", params={"education": "undergrad"}).json()

    assert body["total"] == 1
    assert body["listings"][0]["company"] == "TikTok"
    assert client.get("/api/listings", params={"education": "phd"}).json()["total"] == 0


def test_filters_carry_the_degree_counts(client):
    body = client.get("/api/filters").json()

    assert body["education_counts"] == {"": 1, "undergrad": 1}


def test_the_profile_can_be_saved_and_drives_what_the_dashboard_shows(client):
    """The dashboard is the profile's list. Saving a degree and a level is what
    narrows it, so these have to be one test, not two."""
    saved = client.post(
        "/api/profile",
        json={
            "education": "undergrad",
            "seeking": ["intern"],
            "roles": ["Software Engineer Intern"],
        },
    )

    assert saved.status_code == 200
    assert saved.json()["profile"]["education"] == "undergrad"
    assert saved.json()["profile"]["seeking"] == ["intern"]

    everything = client.get("/api/listings").json()
    matching = client.get("/api/listings", params={"match_profile": "true"}).json()

    assert everything["total"] == 2
    assert [row["company"] for row in matching["listings"]] == ["TikTok"]


def test_a_phd_posting_is_hidden_from_an_undergraduate(client):
    """A listing that asks for more than the user has is not one they can
    apply to, so it is not on their board."""
    from intern_app import db

    conn = db.connect()
    row_id = conn.execute("SELECT id FROM listings WHERE company = 'TikTok'").fetchone()["id"]
    db.set_listing_detail(
        conn, listing_id=row_id, clean_title="SWE", level="intern", education="phd", term=""
    )
    conn.close()

    client.post("/api/profile", json={"education": "undergrad", "seeking": ["intern"]})

    assert client.get("/api/listings", params={"match_profile": "true"}).json()["total"] == 0


def test_a_profile_that_wants_nothing_in_particular_still_sees_everything(client):
    """An empty answer is "no preference", not "match nothing"."""
    client.post("/api/profile", json={"education": "", "seeking": [], "roles": []})

    assert client.get("/api/listings", params={"match_profile": "true"}).json()["total"] == 2


def test_an_unknown_degree_is_refused(client):
    refused = client.post("/api/profile", json={"education": "doctorate-ish"})

    assert refused.status_code == 400


def test_the_form_options_are_served_for_the_dropdowns(client):
    body = client.get("/api/options").json()

    assert [item["key"] for item in body["degrees"]] == ["undergrad", "masters", "phd"]
    assert [item["key"] for item in body["seeking"]] == ["intern", "coop", "new_grad"]


def test_a_tracked_listing_keeps_its_place_on_the_board(client):
    """The point of showing status on the board is to stop a second apply.

    A listing used to leave the board the moment it was tracked, so the board
    could never tell you that you had already been there.
    """
    listing_id = client.get("/api/listings").json()["listings"][0]["id"]

    client.post("/api/status", json={"listing_id": listing_id, "status": "applied"})

    rows = client.get("/api/listings").json()["listings"]
    assert [row["status"] for row in rows if row["id"] == listing_id] == ["applied"]


def test_ignoring_a_listing_removes_it_and_the_filter_brings_it_back(client):
    """Ignore has to hide the row everywhere except the shelf it went to."""
    listing_id = client.get("/api/listings").json()["listings"][0]["id"]

    client.post("/api/status", json={"listing_id": listing_id, "status": "hidden"})

    board = client.get("/api/listings").json()
    assert listing_id not in [row["id"] for row in board["listings"]]

    shelf = client.get("/api/listings?status=hidden").json()
    assert [row["id"] for row in shelf["listings"]] == [listing_id]
    assert shelf["total"] == 1


def test_the_board_counts_follow_a_status_change(client):
    """The chip has to be right the moment the row moves, without a refetch."""
    listing_id = client.get("/api/listings").json()["listings"][0]["id"]

    reply = client.post("/api/status", json={"listing_id": listing_id, "status": "hidden"}).json()

    assert reply["board_counts"]["hidden"] == 1
    assert client.get("/api/filters").json()["board_status_counts"]["hidden"] == 1


def test_an_unknown_status_filter_is_ignored_rather_than_obeyed(client):
    """A junk value must not silently empty the board."""
    body = client.get("/api/listings?status=notastatus").json()

    assert body["total"] == 2


def test_a_background_choice_survives_the_round_trip(client):
    """The picker is only worth having if the choice is still there tomorrow."""
    assert client.get("/api/settings").json()["background"] == "meadow"

    saved = client.post("/api/settings", json={"key": "background", "value": "coast"}).json()

    assert saved["background"] == "coast"
    assert client.get("/api/settings").json()["background"] == "coast"


def test_an_unknown_setting_is_refused(client):
    """A typo must not write a key nothing reads, which would fail silently."""
    reply = client.post("/api/settings", json={"key": "theme", "value": "dark"})

    assert reply.status_code == 400
    assert "unknown setting" in reply.json()["detail"]


def test_a_background_with_no_image_behind_it_is_refused(client):
    """A stored key with no file would render a blank page with no clue why."""
    reply = client.post("/api/settings", json={"key": "background", "value": "volcano"})

    assert reply.status_code == 400
    assert "unknown background" in reply.json()["detail"]


def test_activity_puts_an_application_on_the_day_it_was_sent(client):
    """The chart is only worth drawing if a bar lands on the right day.

    Asserting the shape alone passed while the grouping, the company list and
    the UTC-to-local day conversion could all have been broken, because the
    fixture sends no applications and every count is zero.
    """
    listing_id = client.get("/api/listings").json()["listings"][0]["id"]
    client.post("/api/status", json={"listing_id": listing_id, "status": "applied"})

    body = client.get("/api/activity?days=7").json()

    assert body["days"] == 7
    assert len(body["entries"]) == 7
    today = body["entries"][-1]
    assert today["count"] == 1
    assert today["companies"][0]["company"] in {"TikTok", "TD Bank"}
    assert sum(entry["count"] for entry in body["entries"][:-1]) == 0


def test_moving_an_application_on_does_not_move_its_bar(client):
    """A listing counts on the day it was sent, not the day it last changed."""
    listing_id = client.get("/api/listings").json()["listings"][0]["id"]
    client.post("/api/status", json={"listing_id": listing_id, "status": "applied"})
    client.post("/api/status", json={"listing_id": listing_id, "status": "interviewing"})

    entries = client.get("/api/activity?days=7").json()["entries"]

    assert sum(entry["count"] for entry in entries) == 1


def test_an_unsupported_range_falls_back_to_the_default(client):
    """A junk range must not return an empty chart with no explanation."""
    assert client.get("/api/activity?days=999").json()["days"] == 7
