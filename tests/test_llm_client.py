"""Every billed call must land in `llm_calls`, success or failure.

CLAUDE.md rule 5 is the easiest rule to break silently: the money is spent the
moment the API is called, so a failure after the call still has to show up in
the spend report. These tests fake the SDK, so nothing here hits the network.
"""

import pytest
from pydantic import BaseModel, ValidationError

from intern_app.llm import client

MODEL = "claude-opus-5-5"


class Roles(BaseModel):
    roles: list[str]


class FakeUsage:
    def __init__(self):
        self.input_tokens = 400
        self.output_tokens = 90
        self.cache_read_input_tokens = None
        self.cache_creation_input_tokens = None


class FakeResponse:
    """Shaped like the SDK response the real code reads."""

    def __init__(self, parsed, stop_reason="end_turn"):
        self.parsed_output = parsed
        self.usage = FakeUsage()
        self.stop_reason = stop_reason
        self._request_id = "req_fake123"


def install_fake(monkeypatch, result):
    """Point the client at a fake SDK. `result` is returned or raised."""

    class FakeMessages:
        def parse(self, **_):
            if isinstance(result, Exception):
                raise result
            return result

    class FakeAnthropic:
        def __init__(self, **_):
            self.messages = FakeMessages()

    monkeypatch.setattr(client.anthropic, "Anthropic", FakeAnthropic)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-fake")
    from intern_app import config

    config.settings.cache_clear()


def call(conn):
    return client.call_structured(
        conn, prompt_name="suggest_roles", prompt="hello", output_model=Roles
    )


def logged(conn):
    return conn.execute("SELECT * FROM llm_calls").fetchall()


def test_a_successful_call_is_logged_with_tokens_and_cost(conn, monkeypatch):
    install_fake(monkeypatch, FakeResponse(Roles(roles=["Data Science Intern"])))

    result = call(conn)

    assert result.roles == ["Data Science Intern"]
    rows = logged(conn)
    assert len(rows) == 1
    assert rows[0]["ok"] == 1
    assert rows[0]["input_tokens"] == 400
    assert rows[0]["cost_usd"] > 0
    assert rows[0]["request_id"] == "req_fake123"


def test_an_api_error_is_still_logged(conn, monkeypatch):
    import anthropic

    install_fake(monkeypatch, anthropic.APIConnectionError(request=None))

    with pytest.raises(anthropic.APIError):
        call(conn)

    rows = logged(conn)
    assert len(rows) == 1
    assert rows[0]["ok"] == 0
    assert "APIConnectionError" in rows[0]["error"]


def test_a_reply_that_fails_validation_is_logged_with_its_tokens(conn, monkeypatch):
    """The regression: a pydantic failure left a billed call unlogged."""
    try:
        Roles(roles="not a list")
    except ValidationError as exc:
        install_fake(monkeypatch, exc)

    with pytest.raises(ValidationError):
        call(conn)

    rows = logged(conn)
    assert len(rows) == 1
    assert rows[0]["ok"] == 0
    assert "ValidationError" in rows[0]["error"]


def test_a_refusal_or_cutoff_is_logged_and_charged(conn, monkeypatch):
    """parsed_output is None on a refusal or max_tokens, after being billed."""
    install_fake(monkeypatch, FakeResponse(None, stop_reason="max_tokens"))

    with pytest.raises(client.UnusableReplyError, match="max_tokens"):
        call(conn)

    rows = logged(conn)
    assert len(rows) == 1
    assert rows[0]["ok"] == 0
    assert rows[0]["input_tokens"] == 400
    assert rows[0]["cost_usd"] > 0


def test_no_key_raises_before_spending_anything(conn, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    from intern_app import config

    config.settings.cache_clear()

    with pytest.raises(client.NoApiKeyError):
        call(conn)

    assert logged(conn) == []


def test_load_prompt_fills_placeholders():
    text = client.load_prompt("suggest_roles", major="Applied Math", interests="ML infra")
    assert "Applied Math" in text
    assert "ML infra" in text


def test_a_missing_prompt_file_fails_loudly():
    with pytest.raises(FileNotFoundError, match="no_such_prompt"):
        client.load_prompt("no_such_prompt")
