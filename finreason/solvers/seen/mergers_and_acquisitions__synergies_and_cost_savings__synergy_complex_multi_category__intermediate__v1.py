from fractions import Fraction

from finreason.nums import grab_all, grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.synergies_and_cost_savings.synergy_complex_multi_category.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    a, b = grab_all(r"[Pp]rocurement spends are {N} and {N}", text)
    rate = grab(r"procurement reduction is {N} percent", text) / 100
    it = grab(r"fixed annual IT savings are {N}", text)
    combined = a + b
    proc = combined * rate
    return {"final": proc + it, "slots": {"trace_1": combined, "trace_2": proc}}
