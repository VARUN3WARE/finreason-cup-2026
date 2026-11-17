from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.wacc.inflation_adjusted_capm_wacc.advanced.v1"


def solve(text: str, q: dict) -> dict:
    E = grab(r"common equity E of {N} USD million", text)
    DA = grab(r"debt A value DA of {N} USD million", text)
    DB = grab(r"debt B value DB of {N} USD million", text)
    beta = grab(r"beta is {N}", text)
    rn = grab(r"nominal market return rn is {N} percent", text)
    pi = grab(r"inflation pi is {N} percent", text)
    rf = grab(r"real risk-free rate rf is {N} percent", text)
    ka = grab(r"ka={N} percent", text)
    kb = grab(r"kb={N} percent", text)
    T = grab(r"tax rate T is {N} percent", text)

    rm = 100 * ((1 + rn / 100) / (1 + pi / 100) - 1)
    ke = rf + beta * (rm - rf)
    D = DA + DB
    kd = (DA * ka + DB * kb) / D
    V = E + D
    wE = E / V
    wD = D / V
    wacc = wE * ke + wD * kd * (1 - T / 100)
    return {
        "final": wacc,
        "slots": {
            "real_market_return_percent": rm,
            "capm_real_equity_cost_percent": ke,
            "weighted_real_debt_cost_percent": kd,
        },
    }
