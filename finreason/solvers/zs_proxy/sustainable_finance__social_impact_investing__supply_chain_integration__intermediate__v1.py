from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.social_impact_investing.supply_chain_integration.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    unit_cost = grab(r"originally costs {N} USD per unit", text)
    pct = grab(r"reduce that cost by {N} percent", text)
    fixed = grab(r"fixed saving of {N} USD per unit", text)
    units = grab(r"[Aa]nnual production is {N} units", text)
    pct_saving = unit_cost * pct / 100
    total_per_unit = pct_saving + fixed
    return {"final": units * total_per_unit,
            "slots": {"percentage_saving_trace": pct_saving,
                      "total_saving_per_unit_trace": total_per_unit}}
