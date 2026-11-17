from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.wacc.preferred_capm_wacc.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    e = grab(r"common equity E of {N} USD", text)
    p = grab(r"preferred stock P of {N} USD", text)
    d = grab(r"interest-bearing debt D of {N} USD", text)
    beta = grab(r"common-equity beta is {N}", text)
    rf = grab(r"risk-free rate rf is {N} percent", text)
    rm = grab(r"market return rm is {N} percent", text)
    kp = grab(r"preferred-stock cost kp is {N} percent", text)
    kd = grab(r"pretax debt cost kd is {N} percent", text)
    t = grab(r"tax rate T is {N} percent", text)
    ke = rf + beta * (rm - rf)
    v = e + p + d
    w_e = e / v
    w_p = p / v
    w_d = d / v
    # Only debt gets the tax shield; preferred cost enters pre-tax.
    kd_after = kd * (1 - t / 100)
    wacc = w_e * ke + w_p * kp + w_d * kd_after
    return {
        "final": wacc,
        "slots": {
            "capm_equity_cost_percent": ke,
            "preferred_weight": w_p,
            "after_tax_debt_cost_percent": kd_after,
        },
    }
