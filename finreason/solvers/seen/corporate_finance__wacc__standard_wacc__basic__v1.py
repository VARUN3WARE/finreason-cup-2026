from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.wacc.standard_wacc.basic.v1"


def solve(text: str, q: dict) -> dict:
    e = grab(r"common equity E of {N} USD", text)
    d = grab(r"interest-bearing debt D of {N} USD", text)
    ke = grab(r"cost of equity ke is {N} percent", text)
    kd = grab(r"pretax cost of debt kd is {N} percent", text)
    t = grab(r"tax rate T is {N} percent", text)
    v = e + d
    w_e = e / v
    w_d = d / v
    kd_after = kd * (1 - t / 100)
    wacc = w_e * ke + w_d * kd_after
    return {
        "final": wacc,
        "slots": {
            "total_capital": v,
            "equity_weight": w_e,
            "after_tax_debt_cost_percent": kd_after,
        },
    }
