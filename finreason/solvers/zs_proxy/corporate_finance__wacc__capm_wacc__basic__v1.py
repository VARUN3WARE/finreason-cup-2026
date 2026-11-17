from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.wacc.capm_wacc.basic.v1"


def solve(text: str, q: dict) -> dict:
    E = grab(r"common equity E of {N} USD million", text)
    D = grab(r"interest-bearing debt D of {N} USD million", text)
    beta = grab(r"beta is {N}", text)
    rf = grab(r"risk-free rate rf is {N} percent", text)
    rm = grab(r"market return rm is {N} percent", text)
    kd = grab(r"debt cost kd is {N} percent", text)
    T = grab(r"tax rate T is {N} percent", text)

    mrp = rm - rf
    ke = rf + beta * mrp
    V = E + D
    wE = E / V
    wD = D / V
    wacc = wE * ke + wD * kd * (1 - T / 100)
    return {
        "final": wacc,
        "slots": {
            "market_risk_premium_percent": mrp,
            "capm_equity_cost_percent": ke,
            "debt_weight": wD,
        },
    }
