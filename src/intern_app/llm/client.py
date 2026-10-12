"""The Claude client, and the one path every LLM call takes.

Every call that reaches the API is logged to `llm_calls` with tokens and
computed cost, on success and on every kind of failure. That is a hard rule in
CLAUDE.md: the moment the API is called the money is spent, so a failure after
the call still has to appear in the spend report.
"""

from __future__ import annotations

import sqlite3
from typing import Any

import anthropic
from pydantic import BaseModel

from intern_app import db
from intern_app.config import settings

# A role list or a requirement list is a short answer. Lowering this from the
# usual default is deliberate, not a cost guess. Callers that return one object
# per input — reading forty titles, say — pass a larger ceiling, because hitting
# this one truncates the JSON mid-string and the whole batch is lost after being
# paid for.
MAX_TOKENS = 2048


class NoApiKeyError(RuntimeError):
    """ANTHROPIC_API_KEY is unset, so no LLM step can run."""


class UnusableReplyError(RuntimeError):
    """The call was billed but the reply cannot be used.

    Raised when the model refuses, hits the token ceiling, or returns something
    that does not validate against the expected shape.
    """


def have_api_key() -> bool:
    """Whether LLM steps are available at all.

    Onboarding calls this so the Other button can say it needs a key instead of
    failing mid-form.
    """
    return settings().has("ANTHROPIC_API_KEY")


def load_prompt(name: str, **fields: str) -> str:
    """Read `prompts/<name>.txt` and fill in its placeholders.

    Prompts live in files so that changing one is a reviewable diff.
    """
    path = settings().prompts_dir / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"No prompt named {name!r} at {path}")
    return path.read_text().format(**fields)


def usage_of(response: Any) -> dict[str, int]:
    """Token counts from a response, or zeros when there is no response.

    A request that failed before returning has nothing to report, but a reply
    that arrived and then failed validation does — and that is the case worth
    recording, because it was billed.
    """
    usage = getattr(response, "usage", None)
    if usage is None:
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
        }
    return {
        "input_tokens": usage.input_tokens or 0,
        "output_tokens": usage.output_tokens or 0,
        "cache_read_tokens": usage.cache_read_input_tokens or 0,
        "cache_write_tokens": usage.cache_creation_input_tokens or 0,
    }


def json_format(output_model: type[BaseModel]) -> dict:
    """The response format for a model, as the API's structured outputs want it.

    Pydantic's schema needs `additionalProperties: false` on every object for
    the API to accept it as strict.
    """
    schema = output_model.model_json_schema()
    for definition in [schema, *schema.get("$defs", {}).values()]:
        if definition.get("type") == "object":
            definition["additionalProperties"] = False
    return {"type": "json_schema", "schema": schema}


def call_structured(
    conn: sqlite3.Connection,
    *,
    prompt_name: str,
    prompt: str,
    output_model: type[BaseModel],
    listing_id: int | None = None,
    effort: str = "low",
    max_tokens: int = MAX_TOKENS,
    model: str = "",
) -> BaseModel:
    """Send one prompt, validate the reply against `output_model`, log the call.

    `effort` defaults to low because the calls in this app are short extraction
    and suggestion tasks rather than hard reasoning. Raise it per call site if a
    task needs more thought.

    `model` overrides the configured one for a single call. Reading a job
    description is a long-input, short-output job where the volume of text
    rather than the difficulty is what costs, so that step asks for a smaller
    model. The logged cost is computed from whichever model actually ran.
    """
    if not have_api_key():
        # Nothing was spent, so there is nothing to log.
        raise NoApiKeyError("ANTHROPIC_API_KEY is not set. Add it to .env to use the LLM steps.")

    cfg = settings()
    chosen = model or cfg.model
    client = anthropic.Anthropic(api_key=cfg.require("ANTHROPIC_API_KEY"))
    response = None

    try:
        # `messages.parse` would validate the reply for us, but it raises before
        # handing the response back, so a truncated or invalid reply logs zero
        # tokens and zero cost for a call that was billed in full. Asking for
        # the JSON and validating it here keeps the usage in hand whatever
        # happens, which is what makes the spend report honest.
        response = client.messages.create(
            model=chosen,
            max_tokens=max_tokens,
            output_config={"effort": effort, "format": json_format(output_model)},
            messages=[{"role": "user", "content": prompt}],
        )

        if response.stop_reason == "max_tokens":
            raise UnusableReplyError(
                f"{prompt_name}: reply hit the {max_tokens}-token ceiling and was cut off"
            )
        if response.stop_reason == "refusal":
            raise UnusableReplyError(f"{prompt_name}: the model declined this request")

        text = next((block.text for block in response.content if block.type == "text"), "")
        parsed = output_model.model_validate_json(text)
    except Exception as exc:
        # Deliberately broad: anything at all after the request leaves money
        # spent, and an unlogged call breaks the rule that the spend report is
        # complete. The exception is re-raised untouched.
        db.record_llm_call(
            conn,
            prompt_name=prompt_name,
            model=chosen,
            listing_id=listing_id,
            request_id=getattr(response, "_request_id", "") or "",
            input_text=prompt,
            ok=False,
            error=f"{type(exc).__name__}: {exc}",
            **usage_of(response),
        )
        raise

    db.record_llm_call(
        conn,
        prompt_name=prompt_name,
        model=chosen,
        listing_id=listing_id,
        request_id=response._request_id or "",
        input_text=prompt,
        output_text=parsed.model_dump_json(),
        ok=True,
        **usage_of(response),
    )
    return parsed
