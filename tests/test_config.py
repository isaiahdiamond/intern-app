"""Config must fail loudly on a missing key and never echo a value."""

from pathlib import Path

import pytest

from intern_app.config import DEFAULT_MODEL, MissingConfig, Settings


def make_settings(**env) -> Settings:
    return Settings(
        db_path=Path("data/test.db"),
        model=DEFAULT_MODEL,
        prompts_dir=Path("prompts"),
        companies_file=Path("companies.txt"),
        _env=env,
    )


def test_require_returns_a_set_value():
    assert make_settings(MUSE_API_KEY="abc123").require("MUSE_API_KEY") == "abc123"


def test_require_raises_naming_the_variable():
    with pytest.raises(MissingConfig, match="MUSE_API_KEY is not set"):
        make_settings().require("MUSE_API_KEY")


def test_require_does_not_leak_the_value_in_the_message():
    # Not a credential: a syntactically plausible fake, so the assertion below
    # proves the message does not echo whatever was passed in.
    secret = "sk-ant-not-a-real-key"  # noqa: S105
    with pytest.raises(MissingConfig) as caught:
        make_settings(OTHER=secret).require("ANTHROPIC_API_KEY")
    assert secret not in str(caught.value)


def test_blank_counts_as_unset():
    cfg = make_settings(MUSE_API_KEY="")
    assert cfg.has("MUSE_API_KEY") is False
    with pytest.raises(MissingConfig):
        cfg.require("MUSE_API_KEY")


def test_has_requires_every_name():
    cfg = make_settings(ADZUNA_APP_ID="id")
    assert cfg.has("ADZUNA_APP_ID") is True
    assert cfg.has("ADZUNA_APP_ID", "ADZUNA_APP_KEY") is False


def test_get_falls_back_to_the_default():
    assert make_settings().get("GMAIL_TOKEN_FILE", "token.json") == "token.json"
