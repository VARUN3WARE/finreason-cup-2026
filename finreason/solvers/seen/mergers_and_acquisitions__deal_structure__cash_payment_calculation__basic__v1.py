from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.deal_structure.cash_payment_calculation.basic.v1"


def solve(text: str, q: dict) -> dict:
    total = grab(r"Total deal value is {N} USD", text)
    cash_pct = grab(r"cash portion is {N} percent", text)
    ratio = cash_pct / 100
    return {"final": total * ratio, "slots": {"trace_1": ratio}}
