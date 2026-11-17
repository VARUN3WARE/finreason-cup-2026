from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.risk_management.scenario_planning.interest_rate_impact.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    loan = grab(r"Loan amount is L\s*=\s*{N}", text)
    r = grab(r"rate increase is r\s*=\s*{N}\s*percent", text)
    s = grab(r"sensitivity is s\s*=\s*{N}", text)
    rate_ratio = r / 100
    cost = loan * rate_ratio * s
    return {"final": cost, "slots": {"rate_ratio_trace": rate_ratio}}
