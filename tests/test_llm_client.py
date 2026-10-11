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


class FakeBlock:
    def __init__(self, text):
        self.type = "text"
        self.text = text


class FakeResponse:
    """Shaped like the response `messages.create` returns.

    The client asks for JSON and validates it itself rather than using
    `messages.parse`, so that a truncated or invalid reply still carries its
    usage and is logged with the cost it actually incurred.
    """

    def __init__(self, text, stop_reason="end_turn"):
        self.content = [FakeBlock(text)]
        self.usage = FakeUsage()
        self.stop_reason = stop_reason
        self._request_id = "req_fake123"


def install_fake(monkeypatch, result):
    """Point the client at a fake SDK. `result` is returned or raised."""

    class FakeMessages:
        def create(self, **_):
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
    install_fake(monkeypatch, FakeResponse('{"roles": ["Data Science Intern"]}'))

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
    """A billed call whose reply does not validate must still carry its cost.
    Using the SDK's parse helper logged these at zero, because it raises before
    handing the response back."""
    install_fake(monkeypatch, FakeResponse('{"roles": "not a list"}'))

    with pytest.raises(ValidationError):
        call(conn)

    rows = logged(conn)
    assert len(rows) == 1
    assert rows[0]["ok"] == 0
    assert "ValidationError" in rows[0]["error"]
    assert rows[0]["input_tokens"] == 400
    assert rows[0]["cost_usd"] > 0


def test_a_refusal_or_cutoff_is_logged_and_charged(conn, monkeypatch):
    """A reply cut off at the token ceiling is billed in full and its JSON is
    unusable. This happened for real on a batch of forty titles."""
    install_fake(monkeypatch, FakeResponse('{"roles": ["truncated', stop_reason="max_tokens"))

    with pytest.raises(client.UnusableReplyError, match="ceiling"):
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
