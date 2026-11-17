from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.post-merger_integration.integration_synergy_calculation.basic.v1"


def solve(text: str, q: dict) -> dict:
    a = grab(r"operating cost at Company A is {N}", text)
    b = grab(r"operating cost at Company B is {N}", text)
    rate = grab(r"combined amount by {N} percent", text) / 100
    combined = a + b
    savings = combined * rate
    return {"final": savings, "slots": {"trace_1": combined}}
