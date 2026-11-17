from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.wacc.standard_wacc.basic.v1"


def solve(text: str, q: dict) -> dict:
    E = grab(r"common equity E of {N} USD million", text)
    D = grab(r"interest-bearing debt D of {N} USD million", text)
    ke = grab(r"cost of equity ke is {N} percent", text)
    kd = grab(r"cost of debt kd is {N} percent", text)
    T = grab(r"tax rate T is {N} percent", text)

    V = E + D
    wE = E / V
    wD = D / V
    kd_at = kd * (1 - T / 100)
    wacc = wE * ke + wD * kd_at
    return {
        "final": wacc,
        "slots": {
            "total_capital": V,
            "equity_weight": wE,
            "after_tax_debt_cost_percent": kd_at,
        },
    }
