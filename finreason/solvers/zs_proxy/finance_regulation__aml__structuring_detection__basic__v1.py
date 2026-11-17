"""Structuring detection: count condition = count >= trigger; amount condition = amount < ceiling (strict);
alert (final) = both conditions true."""

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.aml.structuring_detection.basic.v1"


def _tok(b: bool) -> str:
    return "true" if b else "false"


def solve(text: str, q: dict) -> dict:
    count = grab(r"Transaction count is {N}", text)
    amount = grab(r"Each transaction amount in USD is {N}", text)
    trigger = grab(r"count trigger is {N}", text)
    ceiling = grab(r"amount ceiling in USD is {N}", text)
    count_met = count >= trigger
    below = amount < ceiling
    return {
        "final": _tok(count_met and below),
        "slots": {"count_trigger_met": _tok(count_met), "amount_below_ceiling": _tok(below)},
    }
