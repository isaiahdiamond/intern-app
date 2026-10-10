"""Config must fail loudly on a missing key and never echo a value."""

from pathlib import Path

import pytest

from intern_app.config import DEFAULT_MODEL, MissingConfigError, Settings


def make_settings(**env) -> Settings:
    return Settings(
        db_path=Path("data/test.db"),
        model=DEFAULT_MODEL,
        prompts_dir=Path("prompts"),
        _env=env,
    )


def test_require_returns_a_set_value():
    assert make_settings(MUSE_API_KEY="abc123").require("MUSE_API_KEY") == "abc123"


def test_require_raises_without_leaking_the_value():
    # Not a credential: a plausible-looking fake, so the assertion proves the
    # message does not echo whatever was passed in.
    fake = "sk-ant-not-a-real-key"
    with pytest.raises(MissingConfigError, match="ANTHROPIC_API_KEY is not set") as caught:
        make_settings(OTHER=fake).require("ANTHROPIC_API_KEY")
    assert fake not in str(caught.value)


def test_blank_counts_as_unset():
    cfg = make_settings(MUSE_API_KEY="")
    assert cfg.has("MUSE_API_KEY") is False
    with pytest.raises(MissingConfigError):
        cfg.require("MUSE_API_KEY")


def test_has_requires_every_name():
    cfg = make_settings(ADZUNA_APP_ID="id")
    assert cfg.has("ADZUNA_APP_ID") is True
    assert cfg.has("ADZUNA_APP_ID", "ADZUNA_APP_KEY") is False
