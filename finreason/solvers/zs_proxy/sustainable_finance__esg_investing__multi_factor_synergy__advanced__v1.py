from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.esg_investing.multi_factor_synergy.advanced.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"initial cost of {N} USD", text)
    energy_m = grab(r"saves {N} USD per month on energy", text)
    credit = grab(r"receives {N} USD per year", text)
    opex = grab(r"reduces annual operating costs of {N} USD", text)
    red = grab(r"inclusive, by {N} percent", text) / 100
    years = grab(r"runs for {N} years", text)
    energy = energy_m * 12
    eff = opex * red
    total = years * (energy + eff + credit)
    return {
        "final": total - cost,
        "slots": {
            "annual_energy_savings_trace": energy,
            "annual_efficiency_savings_trace": eff,
            "total_savings_trace": total,
        },
    }
