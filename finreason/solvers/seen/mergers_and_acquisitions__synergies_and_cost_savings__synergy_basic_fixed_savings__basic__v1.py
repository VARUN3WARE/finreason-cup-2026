from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.synergies_and_cost_savings.synergy_basic_fixed_savings.basic.v1"


def solve(text: str, q: dict) -> dict:
    a = grab(r"at Company A are {N}", text)
    b = grab(r"at Company B are {N}", text)
    return {"final": a + b, "slots": {}}
