from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.due_diligence.due_diligence_synergy_estimation.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    ra = grab(r"Company A revenue is {N}", text)
    rb = grab(r"Company B revenue is {N}", text)
    s = grab(r"synergy rate is {N} percent", text) / 100
    cost = grab(r"integration cost is {N}", text)
    combined = ra + rb
    gross = combined * s
    return {"final": gross - cost, "slots": {"trace_1": combined, "trace_2": gross}}
