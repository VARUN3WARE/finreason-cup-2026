from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.wacc.preferred_capm_wacc.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    E = grab(r"common equity E of {N} USD million", text)
    P = grab(r"preferred stock P of {N} USD million", text)
    D = grab(r"interest-bearing debt D of {N} USD million", text)
    beta = grab(r"beta is {N}", text)
    rf = grab(r"risk-free rate rf is {N} percent", text)
    rm = grab(r"market return rm is {N} percent", text)
    kp = grab(r"preferred-stock cost kp is {N} percent", text)
    kd = grab(r"debt cost kd is {N} percent", text)
    T = grab(r"tax rate T is {N} percent", text)

    ke = rf + beta * (rm - rf)
    V = E + P + D
    wE = E / V
    wP = P / V
    wD = D / V
    kd_at = kd * (1 - T / 100)
    wacc = wE * ke + wP * kp + wD * kd_at
    return {
        "final": wacc,
        "slots": {
            "capm_equity_cost_percent": ke,
            "preferred_weight": wP,
            "after_tax_debt_cost_percent": kd_at,
        },
    }
