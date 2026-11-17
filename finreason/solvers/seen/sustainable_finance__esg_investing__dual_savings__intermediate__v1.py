from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.esg_investing.dual_savings.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    energy_m = grab(r"saves\s+{N}\s+USD per month on energy", text)
    water_m = grab(r"and\s+{N}\s+USD per month on water", text)
    maint = grab(r"incurs\s+{N}\s+USD of annual maintenance", text)
    incentive = grab(r"receives\s+{N}\s+USD as an annual incentive", text)
    try:
        months = grab(r"constant for\s+{N}\s+months?", text)
    except ValueError:
        months = Fraction(12)
    energy_a = energy_m * months
    water_a = water_m * months
    after_maint = energy_a + water_a - maint
    final = after_maint + incentive
    return {
        "final": final,
        "slots": {
            "annual_energy_savings_trace": energy_a,
            "annual_water_savings_trace": water_a,
            "after_maintenance_trace": after_maint,
        },
    }
