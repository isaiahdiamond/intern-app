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
    rows = board.list_new(board_data, sort="rank")

    assert [row["company"] for row in rows] == ["TD Bank", "TikTok", "Acme Co"]
    assert [row["industry_rank"] for row in rows] == [1, 2, board.UNRANKED]


def test_an_unranked_industry_sorts_last_but_is_not_hidden(board_data):
    """A good role in a fifth-choice industry is still worth seeing."""
    companies = [row["company"] for row in board.list_new(board_data, sort="rank")]

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


def test_the_same_opening_posted_twice_shows_as_one_card(conn, listing):
    """SpaceX posts the same Redmond role four times, each with its own url
    hash. The board shows one, preferring the copy with a description."""
    db.upsert_listings(
        conn,
        [
            listing(
                "https://x.com/dup-a",
                company="SpaceX",
                title="New Grad Engineer",
                location="Redmond, WA",
                full_text=False,
            ),
            listing(
                "https://x.com/dup-b",
                company="SpaceX",
                title="New Grad Engineer",
                location="Redmond, WA",
            ),
            listing(
                "https://x.com/dup-c",
                company="spacex",
                title="new grad engineer",
                location="redmond, wa",
                full_text=False,
            ),
        ],
    )

    rows = [r for r in board.list_new(conn) if r["company"].lower() == "spacex"]

    assert len(rows) == 1
    # The surviving card is the one with the full description.
    assert rows[0]["url"] == "https://x.com/dup-b"
    assert rows[0]["copies"] == 3


def test_the_same_title_in_a_different_city_is_not_a_duplicate(conn, listing):
    """RWS lists "General AI Data Annotator" in California, Dallas and New
    Jersey. All three are real openings."""
    db.upsert_listings(
        conn,
        [
            listing(
                "https://x.com/ca",
                company="RWS",
                title="General AI Data Annotator",
                location="California",
                full_text=False,
            ),
            listing(
                "https://x.com/tx",
                company="RWS",
                title="General AI Data Annotator",
                location="Dallas, TX",
                full_text=False,
            ),
            listing(
                "https://x.com/nj",
                company="RWS",
                title="General AI Data Annotator",
                location="New Jersey",
                full_text=False,
            ),
        ],
    )

    rows = [r for r in board.list_new(conn) if r["company"] == "RWS"]

    assert len(rows) == 3


def test_search_still_reaches_every_copy(conn, listing):
    """Collapsing is a board concern. Nothing is deleted, and Search covers
    every url."""
    db.upsert_listings(
        conn,
        [
            listing(
                "https://x.com/one", company="SpaceX", title="New Grad", location="Redmond, WA"
            ),
            listing(
                "https://x.com/two", company="SpaceX", title="New Grad", location="Redmond, WA"
            ),
        ],
    )

    assert len(board.list_new(conn)) == 1
    assert len([r for r in board.search_listings(conn) if r["company"] == "SpaceX"]) == 2


def test_sorting_by_newest_puts_undated_listings_last(conn, listing):
    """Sorting by rank buries everything but the top industry for 23 pages, so
    a daily pass wants newest first — and a listing with no date must not win."""
    db.upsert_listings(
        conn,
        [
            # Distinct companies, or the duplicate collapse folds them into
            # one card and the sort has nothing left to order.
            listing("https://x.com/old", company="Old Co", posted_at="2025-01-01"),
            listing("https://x.com/new", company="New Co", posted_at="2026-10-09"),
            listing("https://x.com/none", company="Undated Co", posted_at=""),
        ],
    )

    order = [row["url"] for row in board.list_new(conn, sort="newest")]

    assert order == ["https://x.com/new", "https://x.com/old", "https://x.com/none"]


def test_an_unknown_sort_falls_back_rather_than_failing(conn, listing):
    """The sort name comes from a query string, so it is looked up in a fixed
    table and never interpolated."""
    db.upsert_listings(conn, [listing()])

    assert board.order_by("'; DROP TABLE listings; --") == board.SORT_ORDERS[board.DEFAULT_SORT]
    assert board.list_new(conn, sort="nonsense")


def test_filtering_by_role_narrows_to_matching_titles(conn, listing):
    """11 saved roles with no way to filter by them was the biggest functional
    gap in the app."""
    db.upsert_listings(
        conn,
        [
            listing("https://x.com/swe", title="Software Engineer Intern"),
            listing("https://x.com/mech", title="Mechanical Engineering Intern"),
            listing("https://x.com/data", title="Data Science Intern"),
        ],
    )

    titles = [row["title"] for row in board.list_new(conn, roles=["Mechanical Engineer Intern"])]

    assert titles == ["Mechanical Engineering Intern"]


def test_several_roles_are_matched_as_any_not_all(conn, listing):
    db.upsert_listings(
        conn,
        [
            listing("https://x.com/swe", title="Software Engineer Intern"),
            listing("https://x.com/mech", title="Mechanical Engineering Intern"),
            listing("https://x.com/other", title="Marketing Intern"),
        ],
    )

    found = board.list_new(conn, roles=["Software Engineer Intern", "Mechanical Engineer Intern"])

    assert len(found) == 2


def test_an_empty_role_filter_changes_nothing(conn, listing):
    db.upsert_listings(conn, [listing()])

    assert len(board.list_new(conn, roles=[])) == 1
    assert board.count_new(conn, roles=[]) == 1


def test_the_role_filter_counts_match_the_page(conn, listing):
    """The pager reads the count, so it has to apply the same filters."""
    db.upsert_listings(
        conn,
        [
            listing("https://x.com/a", title="Data Science Intern"),
            listing("https://x.com/b", title="Data Science Intern (Summer)"),
            listing("https://x.com/c", title="Software Engineer Intern"),
        ],
    )

    assert board.count_new(conn, roles=["Data Science Intern"]) == 2
    assert len(board.list_new(conn, roles=["Data Science Intern"])) == 2


def clean(conn, listing_id, **fields):
    db.set_listing_detail(
        conn,
        listing_id=listing_id,
        clean_title=fields.get("clean_title", "Software Engineer"),
        level=fields.get("level", "intern"),
        education=fields.get("education", "any"),
        term=fields.get("term", ""),
    )


def test_the_board_shows_the_cleaned_title_and_keeps_the_raw_one(conn, listing):
    """Board titles carry the season, the team and the degree. The raw title is
    never overwritten, so a bad reading can be recomputed."""
    db.upsert_listings(
        conn, [listing(title="Software Engineer Intern - TikTok - 2027 Start - PhD")]
    )
    row_id = conn.execute("SELECT id FROM listings").fetchone()["id"]
    clean(conn, row_id, clean_title="Software Engineer", education="phd")

    row = board.list_new(conn)[0]

    assert row["display_title"] == "Software Engineer"
    assert row["title"] == "Software Engineer Intern - TikTok - 2027 Start - PhD"
    assert row["education"] == "phd"


def test_an_unread_title_falls_back_to_the_raw_one(conn, listing):
    """4,158 listings cannot all be read at once, so the board must work before
    the cleaning pass has run."""
    db.upsert_listings(conn, [listing(title="Raw Title Intern - Summer 2027")])

    row = board.list_new(conn)[0]

    assert row["display_title"] == "Raw Title Intern - Summer 2027"
    assert row["level"] == ""


def test_filtering_by_level_separates_interns_from_new_grads(conn, listing):
    db.upsert_listings(
        conn,
        [
            listing("https://x.com/a", company="A Co", title="SWE Intern"),
            listing("https://x.com/b", company="B Co", title="SWE New Grad"),
            listing("https://x.com/c", company="C Co", title="Senior SWE"),
        ],
    )
    ids = {r["company"]: r["id"] for r in conn.execute("SELECT id, company FROM listings")}
    clean(conn, ids["A Co"], level="intern")
    clean(conn, ids["B Co"], level="new_grad")
    clean(conn, ids["C Co"], level="other")

    assert len(board.list_new(conn, levels=["intern"])) == 1
    assert len(board.list_new(conn, levels=["intern", "new_grad"])) == 2
    assert board.count_new(conn, levels=["new_grad"]) == 1


def test_level_counts_report_unread_titles_separately(conn, listing):
    db.upsert_listings(
        conn,
        [
            listing("https://x.com/a", company="A Co"),
            listing("https://x.com/b", company="B Co"),
        ],
    )
    first = conn.execute("SELECT id FROM listings WHERE company = 'A Co'").fetchone()["id"]
    clean(conn, first, level="intern")

    counts = board.level_counts(conn)

    assert counts["intern"] == 1
    assert counts[""] == 1


def test_the_board_leads_with_the_newest_listing(conn, listing):
    """Ordering by industry rank buried everything else for 23 pages, so the
    default a daily pass gets is newest first."""
    db.upsert_listings(
        conn,
        [
            listing("https://x.com/old", company="Old Co", posted_at="2025-01-01"),
            listing("https://x.com/new", company="New Co", posted_at="2026-10-09"),
        ],
    )

    assert [row["company"] for row in board.list_new(conn)] == ["New Co", "Old Co"]


def test_a_manual_job_lands_in_the_tracker_not_the_board(conn):
    """Most of what I apply to comes through a source. A referral does not, and
    the tracker is not the whole picture unless it holds those too."""
    listing_id = board.add_manual_listing(
        conn,
        title="Software Engineer Intern",
        company="Acme",
        location="Boston, MA",
        status="applied",
        notes="Referred by a friend",
    )

    tracked = board.list_tracked(conn)

    assert [row["id"] for row in tracked] == [listing_id]
    assert tracked[0]["company"] == "Acme"
    assert tracked[0]["source"] == "manual"
    assert tracked[0]["notes"] == "Referred by a friend"
    assert listing_id not in [row["id"] for row in board.list_new(conn)]


def test_two_manual_jobs_with_no_link_do_not_collide(conn):
    """Listings dedupe on url, and a manual entry need not have one."""
    first = board.add_manual_listing(conn, title="SWE Intern", company="Acme")
    second = board.add_manual_listing(conn, title="Data Intern", company="Globex")

    assert first != second
    assert len(board.list_tracked(conn)) == 2


def test_a_manual_job_needs_a_title_and_a_company(conn):
    with pytest.raises(ValueError, match="title and a company"):
        board.add_manual_listing(conn, title="", company="Acme")
    with pytest.raises(ValueError, match="title and a company"):
        board.add_manual_listing(conn, title="SWE Intern", company="  ")
