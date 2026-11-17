from fractions import Fraction
from finreason.nums import grab, grab_all

TEMPLATE_ID = "fp.mergers_and_acquisitions.synergies_and_cost_savings.synergy_complex_multi_category.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    a, b = grab_all(r"Procurement spends are {N} and {N} USD million", text)
    rate = grab(r"procurement reduction is {N} percent", text) / 100
    it = grab(r"fixed annual IT savings are {N} USD million", text)
    combined = a + b
    proc = combined * rate
    return {"final": proc + it, "slots": {"trace_1": combined, "trace_2": proc}}
