from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.wacc.weighted_debt_wacc.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    E = grab(r"common equity E of {N} USD million", text)
    Ds = grab(r"senior debt Ds of {N} USD million", text)
    ks = grab(r"pretax cost ks of {N} percent", text)
    Du = grab(r"subordinated debt Du of {N} USD million", text)
    ku = grab(r"pretax cost ku of {N} percent", text)
    ke = grab(r"common-equity cost ke is {N} percent", text)
    T = grab(r"tax rate T is {N} percent", text)

    D = Ds + Du
    kd = (Ds * ks + Du * ku) / D
    V = E + D
    wE = E / V
    wD = D / V
    wacc = wE * ke + wD * kd * (1 - T / 100)
    return {
        "final": wacc,
        "slots": {
            "total_debt": D,
            "weighted_debt_cost_percent": kd,
            "debt_weight": wD,
        },
    }
