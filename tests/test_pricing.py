import pytest

from intern_app.llm import pricing


def test_cost_of_a_typical_extraction_call():
    # 8k input, 500 output on Opus 5.5: 8000*4/1e6 + 500*20/1e6
    cost = pricing.cost_usd("claude-opus-5-5", input_tokens=8000, output_tokens=500)
    assert cost == pytest.approx(0.042)


def test_cache_reads_are_cheaper_and_cache_writes_dearer_than_fresh_input():
    fresh = pricing.cost_usd("claude-opus-5-5", input_tokens=10_000)
    cached = pricing.cost_usd("claude-opus-5-5", cache_read_tokens=10_000)
    written = pricing.cost_usd("claude-opus-5-5", cache_write_tokens=10_000)

    assert cached < fresh < written


def test_an_unpriced_model_raises_rather_than_logging_a_wrong_cost():
    with pytest.raises(pricing.UnknownModelError, match=r"Add it to llm\.pricing\.PRICES"):
        pricing.cost_usd("some-future-model", input_tokens=100)
