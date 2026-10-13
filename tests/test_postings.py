from intern_app import db


def test_a_posting_restriction_survives_the_write(conn, listing):
    """What only the body says — citizenship and years — has to reach the row.

    The prompt asks for both and the call is billed for both, so dropping them
    on the way to the database means paying twice for the same answer.
    """
    db.upsert_listings(conn, [listing(title="Systems Engineer Intern")])
    listing_id = conn.execute("SELECT id FROM listings").fetchone()["id"]

    db.set_listing_detail(
        conn,
        listing_id=listing_id,
        clean_title="Systems Engineer",
        level="intern",
        education="undergrad",
        term="Summer 2027",
        years_experience=2,
        citizenship="clearance",
    )

    row = conn.execute(
        "SELECT years_experience, citizenship FROM listing_details WHERE listing_id = ?",
        (listing_id,),
    ).fetchone()
    assert row["years_experience"] == 2
    assert row["citizenship"] == "clearance"
