from fractions import Fraction

from finreason.nums import grab_all, grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.synergies_and_cost_savings.synergy_basic_cost_reduction.basic.v1"


def solve(text: str, q: dict) -> dict:
    a, b = grab_all(r"cost bases are {N} and {N}", text)
    rate = grab(r"combined cost by {N} percent", text) / 100
    combined = a + b
    # Annual cost savings = combined cost base x reduction ratio (sign preserved).
    savings = combined * rate
    return {"final": savings, "slots": {"trace_1": combined}}
