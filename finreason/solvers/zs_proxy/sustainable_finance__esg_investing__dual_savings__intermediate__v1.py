from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.sustainable_finance.esg_investing.dual_savings.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    energy_m = grab(r"saves {N} USD per month on energy", text)
    water_m = grab(r"and {N} USD per month on water", text)
    maint = grab(r"incurs {N} USD of annual maintenance", text)
    incentive = grab(r"receives {N} USD as an annual incentive", text)
    try:
        months = grab(r"constant for {N} months", text)
    except ValueError:
        months = 12
    energy = energy_m * months
    water = water_m * months
    after_maint = energy + water - maint
    net = after_maint + incentive
    return {
        "final": net,
        "slots": {
            "annual_energy_savings_trace": energy,
            "annual_water_savings_trace": water,
            "after_maintenance_trace": after_maint,
        },
    }
