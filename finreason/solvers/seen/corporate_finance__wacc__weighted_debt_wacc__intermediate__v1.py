from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.wacc.weighted_debt_wacc.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    e = grab(r"common equity E of {N} USD", text)
    ds = grab(r"senior debt Ds of {N} USD", text)
    ks = grab(r"pretax cost ks of {N} percent", text)
    du = grab(r"subordinated debt Du of {N} USD", text)
    ku = grab(r"pretax cost ku of {N} percent", text)
    ke = grab(r"common-equity cost ke is {N} percent", text)
    t = grab(r"tax rate T is {N} percent", text)
    d = ds + du
    kd = (ds * ks + du * ku) / d
    v = e + d
    w_e = e / v
    w_d = d / v
    wacc = w_e * ke + w_d * kd * (1 - t / 100)
    return {
        "final": wacc,
        "slots": {
            "total_debt": d,
            "weighted_debt_cost_percent": kd,
            "debt_weight": w_d,
        },
    }
