from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.post-merger_integration.integration_synergy_calculation.basic.v1"


def solve(text: str, q: dict) -> dict:
    a = grab(r"[Dd]uplicate operating cost at Company A is {N} USD million", text)
    b = grab(r"[Dd]uplicate operating cost at Company B is {N} USD million", text)
    rate = grab(r"reduces their combined amount by {N} percent", text) / 100
    combined = a + b
    savings = combined * rate
    return {"final": savings, "slots": {"trace_1": combined}}
