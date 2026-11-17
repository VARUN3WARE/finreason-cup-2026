from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.mergers_and_acquisitions.deal_structure.earnout_with_bonus_calculation.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    base = grab(r"Base price is {N} USD", text)
    max_basic = grab(r"maximum basic earn-out is {N} USD", text)
    target = grab(r"target revenue is {N} USD", text)
    actual = grab(r"actual revenue is {N} USD", text)
    rate = grab(r"bonus rate is {N} percent", text) / 100
    cap = grab(r"bonus cap is {N} USD", text)
    thr_pct = grab(r"bonus threshold is {N} percent of target revenue", text)

    basic = min(max_basic * actual / target, max_basic)
    threshold = target * thr_pct / 100
    excess = max(actual - threshold, Fraction(0))
    bonus = min(excess * rate, cap)
    total = base + basic + bonus
    return {"final": total, "slots": {"trace_1": basic, "trace_2": bonus}}
