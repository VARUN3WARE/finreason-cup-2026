from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.sustainability_reporting.dual_operational_savings.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    e_cost = grab(r"energy cost (?:of )?(?:USD )?{N}\s*USD", text)
    e_pct = grab(r"energy cost[^.]*?reduced by {N}\s*percent", text)
    w_cost = grab(r"waste-management cost (?:of )?(?:USD )?{N}\s*USD", text)
    w_pct = grab(r"waste-management cost[^.]*?reduced by {N}\s*percent", text)
    energy = e_cost * e_pct / 100
    waste = w_cost * w_pct / 100
    return {
        "final": energy + waste,
        "slots": {"energy_savings_trace": energy, "waste_savings_trace": waste},
    }
