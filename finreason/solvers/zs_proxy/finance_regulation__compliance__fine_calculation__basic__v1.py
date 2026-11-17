"""Fine = violation count * fine per violation (exact), final rounded by the framework."""
from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.compliance.fine_calculation.basic.v1"


def solve(text: str, q: dict) -> dict:
    count = grab(r"Violation count is {N}", text)
    per = grab(r"Fine per violation in USD is {N}", text)
    fine = count * per
    slots = {}
    for s in q["trace_spec"]["slots"]:  # template defines no slots; fill defensively if one appears
        slots[s["slot_id"]] = fine
    return {"final": fine, "slots": slots}
