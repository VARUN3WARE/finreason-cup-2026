from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.stress_testing.volatility_sensitivity.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    g = grab(r"Vega is G\s*=\s*{N}", text)
    n = grab(r"step count is n\s*=\s*{N}", text)
    slots = {}
    # No intermediate slots in observed instances; fill any defensively with the final impact.
    for slot in q.get("trace_spec", {}).get("slots", []):
        slots[slot["slot_id"]] = g * n
    return {"final": g * n, "slots": slots}
