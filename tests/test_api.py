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
