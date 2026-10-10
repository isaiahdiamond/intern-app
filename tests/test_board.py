"""Ordering by industry preference, and the status lifecycle."""

import pytest

from intern_app import board, db, profile


@pytest.fixture
def board_data(conn, listing):
    """Three companies in three industries, with a profile that ranks two."""
    db.upsert_listings(
        conn,
        [
            listing("https://x.com/a", company="TD Bank", title="Quant Intern"),
            listing("https://x.com/b", company="TikTok", title="Software Engineer Intern"),
            listing("https://x.com/c", company="Acme Co", title="Data Intern"),
        ],
    )
    db.set_company_industry(conn, "TD Bank", "Finance & Trading")
    db.set_company_industry(conn, "TikTok", "Software & Internet")
    db.set_company_industry(conn, "Acme Co", "Gaming")
    profile.save_profile(
        conn,
        school="Example U",
        major="Applied Math & CS",
        roles=[("Software Engineer Intern", "chip")],
        industries=["Finance & Trading", "Software & Internet"],
    )
    return conn


def test_listings_sort_by_industry_preference(board_data):
    rows = board.list_new(board_data)

    assert [row["company"] for row in rows] == ["TD Bank", "TikTok", "Acme Co"]
    assert [row["industry_rank"] for row in rows] == [1, 2, board.UNRANKED]


def test_an_unranked_industry_sorts_last_but_is_not_hidden(board_data):
    """A good role in a fifth-choice industry is still worth seeing."""
    companies = [row["company"] for row in board.list_new(board_data)]

    assert "Acme Co" in companies
    assert companies[-1] == "Acme Co"


def test_the_industry_filter_narrows_the_list(board_data):
    rows = board.list_new(board_data, industry="Finance & Trading")

    assert [row["company"] for row in rows] == ["TD Bank"]


def test_acting_on_a_listing_takes_it_off_the_new_list(board_data):
    listing_id = board.list_new(board_data)[0]["id"]

    board.set_status(board_data, listing_id, "applied")

    assert listing_id not in [row["id"] for row in board.list_new(board_data)]
    assert [row["status"] for row in board.list_tracked(board_data)] == ["applied"]


def test_every_status_change_is_kept_as_history(board_data):
    listing_id = board.list_new(board_data)[0]["id"]

    for status in ("saved", "applied", "interviewing"):
        board.set_status(board_data, listing_id, status)

    assert [row["status"] for row in board.history_for(board_data, listing_id)] == [
        "saved",
        "applied",
        "interviewing",
    ]


def test_hiding_a_listing_keeps_it_out_of_both_lists(board_data):
    listing_id = board.list_new(board_data)[0]["id"]

    board.set_status(board_data, listing_id, "hidden")

    assert listing_id not in [row["id"] for row in board.list_new(board_data)]
    assert listing_id not in [row["id"] for row in board.list_tracked(board_data)]


def test_an_unknown_status_is_refused(board_data):
    listing_id = board.list_new(board_data)[0]["id"]

    with pytest.raises(ValueError, match="status must be one of"):
        board.set_status(board_data, listing_id, "ghosted")


def test_search_matches_title_company_or_location(board_data):
    assert len(board.search_listings(board_data, text="Software")) == 1
    assert len(board.search_listings(board_data, text="TikTok")) == 1
    assert len(board.search_listings(board_data, text="nothing here")) == 0


def test_search_sees_listings_the_dashboard_has_dropped(board_data):
    """The Search tab covers everything stored, whatever its status."""
    listing_id = board.list_new(board_data)[0]["id"]
    board.set_status(board_data, listing_id, "rejected")

    assert len(board.search_listings(board_data)) == 3
    assert len(board.search_listings(board_data, status="rejected")) == 1


def test_a_date_filter_drops_stale_postings(board_data, listing):
    """Sources happily return a posting from last year."""
    db.upsert_listings(
        board_data, [listing("https://x.com/old", company="TikTok", posted_at="2024-01-15")]
    )

    recent = board.list_new(board_data, days=30)

    assert "https://x.com/old" not in [row["url"] for row in recent]


def test_counts_feed_the_tab_badges(board_data):
    listing_id = board.list_new(board_data)[0]["id"]
    board.set_status(board_data, listing_id, "saved")

    counts = board.status_counts(board_data)

    assert counts["new"] == 2
    assert counts["saved"] == 1
