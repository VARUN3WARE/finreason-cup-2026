from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.scenario_planning.operating_cost_increase.basic.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"[Ii]nitial operating cost is\s+C\s*=\s*{N}", text)
    g = grab(r"increase is\s+g\s*=\s*{N}\s*percent", text)
    multiple = 1 + g / 100
    return {"final": cost * multiple, "slots": {"growth_multiple_trace": multiple}}
