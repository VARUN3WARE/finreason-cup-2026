"""Risk score = control failure count * risk points per failure (exact), final rounded by the framework."""
from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.compliance.risk_score.basic.v1"


def solve(text: str, q: dict) -> dict:
    count = grab(r"Control failure count is {N}", text)
    per = grab(r"Risk points per failure (?:are|is) {N}", text)
    score = count * per
    slots = {}
    for s in q["trace_spec"]["slots"]:  # template defines no slots; fill defensively if one appears
        slots[s["slot_id"]] = score
    return {"final": score, "slots": slots}
