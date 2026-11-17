from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.sustainability_reporting.dual_operational_savings.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    energy_cost = grab(r"annual energy cost {N} USD", text)
    energy_pct = grab(r"annual energy cost .*?reduced by {N} percent", text)
    waste_cost = grab(r"annual waste-management cost {N} USD", text)
    waste_pct = grab(r"annual waste-management cost .*?reduced by {N} percent", text)
    energy_sav = energy_cost * energy_pct / 100
    waste_sav = waste_cost * waste_pct / 100
    return {
        "final": energy_sav + waste_sav,
        "slots": {"energy_savings_trace": energy_sav, "waste_savings_trace": waste_sav},
    }
