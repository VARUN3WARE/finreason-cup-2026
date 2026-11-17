from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.esg_investing.multi_factor_synergy.advanced.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"initial cost of\s+{N}\s+USD", text)
    energy_m = grab(r"saves\s+{N}\s+USD per month on energy", text)
    credit = grab(r"receives\s+{N}\s+USD per year", text)
    opcost = grab(r"reduces annual operating costs of\s+{N}\s+USD", text)
    red = grab(r"operating costs of\s+{N}\s+USD.*?\bby\s+{N}\s+percent", text, group=2) / 100
    years = grab(r"runs for\s+{N}\s+years?", text)
    energy_a = energy_m * 12
    eff_a = opcost * red
    total = years * (energy_a + eff_a + credit)
    return {
        "final": total - cost,
        "slots": {
            "annual_energy_savings_trace": energy_a,
            "annual_efficiency_savings_trace": eff_a,
            "total_savings_trace": total,
        },
    }
