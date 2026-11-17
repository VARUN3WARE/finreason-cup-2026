from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.due_diligence.due_diligence_synergy_estimation.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    rev_a = grab(r"Company A revenue is {N}", text)
    rev_b = grab(r"Company B revenue is {N}", text)
    rate = grab(r"synergy rate is {N} percent", text) / 100
    cost = grab(r"integration cost is {N}", text)
    combined = rev_a + rev_b
    gross = combined * rate
    # Net benefit keeps its sign (negative = first-year net cost).
    return {
        "final": gross - cost,
        "slots": {"trace_1": combined, "trace_2": gross},
    }
