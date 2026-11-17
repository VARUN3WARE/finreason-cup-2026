from fractions import Fraction
from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.mergers_and_acquisitions.synergies_and_cost_savings.synergy_basic_cost_reduction.basic.v1"


def solve(text: str, q: dict) -> dict:
    a, b = grab_all(r"cost bases are {N} and {N} USD million", text)
    rate = grab(r"reduce their combined cost by {N} percent", text) / 100
    combined = a + b
    return {"final": combined * rate, "slots": {"trace_1": combined}}
