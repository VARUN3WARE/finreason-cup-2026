"""Delayed fine: total = base fine + delay days * daily penalty."""
from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.compliance.delayed_fine.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    base = grab(r"Base fine in USD is {N}", text)
    days = grab(r"Delay in whole days is {N}", text)
    daily = grab(r"Daily penalty in USD per day is {N}", text)
    penalty = days * daily
    return {"final": base + penalty, "slots": {"delay_penalty_usd": penalty}}
