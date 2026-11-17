from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.wacc.capm_wacc.basic.v1"


def solve(text: str, q: dict) -> dict:
    e = grab(r"common equity E of {N} USD", text)
    d = grab(r"interest-bearing debt D of {N} USD", text)
    beta = grab(r"common-equity beta is {N}", text)
    rf = grab(r"risk-free rate rf is {N} percent", text)
    rm = grab(r"market return rm is {N} percent", text)
    kd = grab(r"pretax debt cost kd is {N} percent", text)
    t = grab(r"tax rate T is {N} percent", text)
    # All rates are kept in percent units, as in the stated formulas.
    mrp = rm - rf
    ke = rf + beta * mrp
    v = e + d
    w_e = e / v
    w_d = d / v
    wacc = w_e * ke + w_d * kd * (1 - t / 100)
    return {
        "final": wacc,
        "slots": {
            "market_risk_premium_percent": mrp,
            "capm_equity_cost_percent": ke,
            "debt_weight": w_d,
        },
    }
