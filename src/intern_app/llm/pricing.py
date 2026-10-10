"""Model prices and the cost computation used when logging an LLM call.

Prices are USD per million tokens, as published for the first-party Claude API.
They are recorded into `llm_calls.cost_usd` at write time, so a later edit here
never rewrites what past calls cost.
"""

from __future__ import annotations

from dataclasses import dataclass

PER_MILLION = 1_000_000


@dataclass(frozen=True)
class Price:
    input_usd: float
    output_usd: float
    cache_read_usd: float
    cache_write_usd: float


# Published first-party Claude API rates, USD per million tokens, as of
# 2026-10-10. Cache writes bill at ~1.25x the input rate; cache reads at the
# model's published cache-read rate. Re-check against Anthropic's pricing page
# before trusting a spend report, and add a row rather than reusing a near match.
PRICES: dict[str, Price] = {
    "claude-opus-5-5": Price(4.00, 20.00, 0.20, 5.00),
    "claude-opus-5": Price(5.00, 25.00, 0.50, 6.25),
    "claude-sonnet-5-5": Price(2.00, 10.00, 0.20, 2.50),
    "claude-haiku-5-5": Price(0.10, 0.50, 0.01, 0.125),
}


class UnknownModelError(KeyError):
    """No price on file for this model, so cost cannot be computed honestly."""


def cost_usd(
    model: str,
    *,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cache_read_tokens: int = 0,
    cache_write_tokens: int = 0,
) -> float:
    """Dollar cost of one call.

    Raises `UnknownModelError` rather than guessing: a silently wrong cost in the log
    is worse than a loud failure, because the log is what the spend report reads.
    """
    try:
        price = PRICES[model]
    except KeyError as exc:
        raise UnknownModelError(
            f"No price on file for {model!r}. Add it to llm.pricing.PRICES."
        ) from exc

    return (
        input_tokens * price.input_usd
        + output_tokens * price.output_usd
        + cache_read_tokens * price.cache_read_usd
        + cache_write_tokens * price.cache_write_usd
    ) / PER_MILLION
