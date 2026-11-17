"""Compliance fine = violation count * fine per violation (exact; framework rounds final)."""

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.compliance.fine_calculation.basic.v1"


def solve(text: str, q: dict) -> dict:
    count = grab(r"Violation count is {N}", text)
    per = grab(r"Fine per violation in USD is {N}", text)
    return {"final": count * per, "slots": {}}
