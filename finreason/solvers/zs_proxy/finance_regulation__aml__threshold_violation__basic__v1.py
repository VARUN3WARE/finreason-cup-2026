"""Threshold violation: signed excess = amount - threshold; breach (final) = amount >= threshold."""

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.aml.threshold_violation.basic.v1"


def _tok(b: bool) -> str:
    return "true" if b else "false"


def solve(text: str, q: dict) -> dict:
    amount = grab(r"transaction amount in USD is {N}", text)
    threshold = grab(r"scenario threshold in USD is {N}", text)
    excess = amount - threshold
    return {"final": _tok(amount >= threshold), "slots": {"amount_excess": excess}}
