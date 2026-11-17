from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.social_impact_investing.supply_chain_integration.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    unit_cost = grab(r"originally costs (?:USD )?{N}(?: USD)? per unit", text)
    red = grab(r"reduce that cost by {N} percent", text) / 100
    fixed = grab(r"fixed saving of (?:USD )?{N}(?: USD)? per unit", text)
    units = grab(r"[Aa]nnual production is {N} units", text)
    pct_saving = unit_cost * red
    total_unit = pct_saving + fixed
    return {
        "final": units * total_unit,
        "slots": {
            "percentage_saving_trace": pct_saving,
            "total_saving_per_unit_trace": total_unit,
        },
    }
