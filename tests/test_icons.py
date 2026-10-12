"""Working out which domain belongs to a company, and caching its favicon."""

from intern_app import icons
from intern_app.llm import domains


def test_a_company_posting_on_its_own_site_needs_no_guess():
    urls = ["https://careers.garmin.com/jobs/123", "https://job-boards.greenhouse.io/acme/4"]

    assert icons.domain_from_urls(urls) == "garmin.com"


def test_an_applicant_tracking_host_is_not_a_company_domain():
    """Every one of these is a job board. `nvidia.wd5.myworkdayjobs.com` names
    the company in the subdomain but the domain still belongs to Workday."""
    urls = [
        "https://job-boards.greenhouse.io/figma/jobs/1",
        "https://jobs.ashbyhq.com/openai/2",
        "https://nvidia.wd5.myworkdayjobs.com/careers/job/3",
        "https://www.adzuna.com/land/ad/4",
    ]

    assert icons.domain_from_urls(urls) == ""


def test_a_country_suffix_keeps_three_labels():
    assert icons.registrable("careers.bbc.co.uk") == "bbc.co.uk"
    assert icons.registrable("jobs.apple.com") == "apple.com"


def test_only_companies_without_a_row_are_looked_up(conn, listing):
    from intern_app import db

    db.upsert_listings(
        conn,
        [
            listing("https://x.com/a", company="Acme"),
            listing("https://x.com/b", company="Globex"),
        ],
    )
    icons.save_icon(conn, company="Acme", domain="acme.com", domain_from="claude", error="HTTP 404")

    pending = [row["company"] for row in icons.companies_needing_icon(conn)]

    assert pending == ["Globex"]


def test_a_company_we_found_nothing_for_is_not_retried(conn, listing):
    """A miss is stored so the lookup does not run again on every page load."""
    from intern_app import db

    db.upsert_listings(conn, [listing(company="Acme")])
    icons.save_icon(conn, company="Acme", domain="", domain_from="", error="no domain")

    assert icons.companies_needing_icon(conn) == []
    assert icons.read_icon(conn, "Acme") is None


def test_only_a_stored_image_is_served(conn, listing):
    from intern_app import db

    db.upsert_listings(conn, [listing(company="Acme")])
    icons.save_icon(
        conn,
        company="Acme",
        domain="acme.com",
        domain_from="url",
        image=b"\x00icon",
        content_type="image/png",
        ok=True,
    )

    row = icons.read_icon(conn, "Acme")

    assert row["image"] == b"\x00icon"
    assert row["content_type"] == "image/png"


def test_a_domain_is_cleaned_however_the_reply_writes_it():
    assert domains.clean_domain("https://www.Nvidia.com/careers") == "nvidia.com"
    assert domains.clean_domain("  SPGlobal.com ") == "spglobal.com"


def test_an_answer_that_is_not_a_domain_is_dropped():
    """A wrong logo is worse than no logo, so anything unusable becomes "" and
    the company is recorded as a miss instead."""
    assert domains.clean_domain("I don't know") == ""
    assert domains.clean_domain("acme") == ""
    assert domains.clean_domain("") == ""
