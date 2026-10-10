"""LinkedIn job alerts, parsed from a real alert email.

The fixture is a real message with the recipient's address, name, LinkedIn
headline and every per-recipient token removed. No test opens a mailbox.
"""

from pathlib import Path

import pytest

from intern_app.sources import linkedin_mail

FIXTURE = Path(__file__).parent / "fixtures" / "linkedin_alert.txt"


@pytest.fixture(scope="module")
def alert_text():
    return FIXTURE.read_text()


def test_one_alert_holds_several_jobs(alert_text):
    """A digest lists five jobs, not one, so every block has to be read."""
    jobs = linkedin_mail.parse_alert(alert_text)

    assert len(jobs) == 5
    assert [job["company"] for job in jobs] == ["FIS", "AMD", "CSX", "New York Life", "FIS"]


def test_each_job_has_a_title_company_and_location(alert_text):
    for job in linkedin_mail.parse_alert(alert_text):
        assert job["title"]
        assert job["company"]
        assert job["location"]


def test_the_apply_url_drops_every_tracking_parameter(alert_text):
    """The mail links carry otpToken and midToken, which identify my email
    account. Only the job id is kept and the public url is rebuilt from it."""
    for job in linkedin_mail.parse_alert(alert_text):
        assert job["url"].startswith("https://www.linkedin.com/jobs/view/")
        assert "?" not in job["url"]
        for token in ("otpToken", "midToken", "midSig", "trackingId", "trk=", "eid="):
            assert token not in job["url"]


def test_canonical_url_is_built_from_the_id_alone():
    assert linkedin_mail.canonical_url("4468838404") == (
        "https://www.linkedin.com/jobs/view/4468838404/"
    )


def test_chrome_lines_are_not_mistaken_for_job_detail(alert_text):
    """ "This company is actively hiring" and the alert heading sit in the same
    block as the job, so they have to be skipped."""
    jobs = linkedin_mail.parse_alert(alert_text)

    titles = [job["title"] for job in jobs]
    assert not any("actively hiring" in title.lower() for title in titles)
    assert not any(title.lower().startswith("your job alert") for title in titles)


def test_alerted_jobs_are_never_full_text(alert_text):
    """The alert carries no description, and the posting must not be fetched."""
    job = linkedin_mail.parse_alert(alert_text)[0]

    listing = linkedin_mail.to_listing(job)

    assert listing["full_text"] is False
    assert listing["description"] == ""
    assert listing["source"] == "linkedin_mail"


def test_a_real_listing_normalizes(alert_text):
    listing = linkedin_mail.to_listing(linkedin_mail.parse_alert(alert_text)[0])

    assert listing["company"] == "FIS"
    assert listing["location"] == "Jacksonville, FL"
    assert listing["title"] == "Data Analytics & AI Intern Pipeline"


def test_text_with_no_job_links_parses_to_nothing():
    assert linkedin_mail.parse_alert("Someone viewed your profile\n\nSee more") == []


def test_only_the_job_alert_sender_is_searched():
    """Other LinkedIn mail — profile views, invitations, messages — must never
    be fetched, and neither must anything else in the mailbox."""
    assert linkedin_mail.ALERT_SENDER == "jobalerts-noreply@linkedin.com"


def test_the_fixture_carries_no_personal_detail(alert_text):
    """A committed fixture must not leak the mailbox owner."""
    for forbidden in ("@yahoo.com", "Isaiah", "Diamond", "intended for", "Aircrewman"):
        assert forbidden not in alert_text
