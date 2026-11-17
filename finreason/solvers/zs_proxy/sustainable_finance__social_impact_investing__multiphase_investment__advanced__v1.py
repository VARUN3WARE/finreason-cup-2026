from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.social_impact_investing.multiphase_investment.advanced.v1"


def solve(text: str, q: dict) -> dict:
    op_cost = grab(r"Phase 1 starts with operating cost {N} USD", text)
    p1_pct = grab(r"reduces it by {N} percent", text)
    per_unit = grab(r"Phase 2 saves {N} USD per unit", text)
    units = grab(r"across {N} units", text)
    sub_pct = grab(r"subsidy equal to {N} percent", text)
    proj_cost = grab(r"of project cost {N} USD", text)
    s1 = op_cost * p1_pct / 100
    s2 = per_unit * units
    s3 = proj_cost * sub_pct / 100
    return {"final": s1 + s2 + s3,
            "slots": {"phase1_savings_trace": s1, "phase2_savings_trace": s2,
                      "phase3_subsidy_trace": s3}}
