from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.social_impact_investing.multiphase_investment.advanced.v1"


def solve(text: str, q: dict) -> dict:
    op_cost = grab(r"Phase 1 starts with operating cost (?:of )?(?:USD )?{N}", text)
    red = grab(r"Phase 1.*?reduces it by {N} percent", text) / 100
    per_unit = grab(r"Phase 2 saves (?:USD )?{N}(?: USD)? per unit", text)
    units = grab(r"across {N} units", text)
    sub_rate = grab(r"subsidy equal to {N} percent", text) / 100
    proj_cost = grab(r"of project cost (?:of )?(?:USD )?{N}", text)
    p1 = op_cost * red
    p2 = per_unit * units
    p3 = sub_rate * proj_cost
    return {
        "final": p1 + p2 + p3,
        "slots": {
            "phase1_savings_trace": p1,
            "phase2_savings_trace": p2,
            "phase3_subsidy_trace": p3,
        },
    }
