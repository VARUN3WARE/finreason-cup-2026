"""Compliance risk score = control failure count * risk points per failure."""

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.compliance.risk_score.basic.v1"


def solve(text: str, q: dict) -> dict:
    count = grab(r"Control failure count is {N}", text)
    pts = grab(r"Risk points per failure (?:are|is) {N}", text)
    return {"final": count * pts, "slots": {}}
