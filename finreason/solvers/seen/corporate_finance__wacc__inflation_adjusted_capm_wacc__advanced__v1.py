from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.corporate_finance.wacc.inflation_adjusted_capm_wacc.advanced.v1"


def solve(text: str, q: dict) -> dict:
    e = grab(r"common equity E of {N} USD", text)
    da = grab(r"debt A value DA of {N} USD", text)
    db = grab(r"debt B value DB of {N} USD", text)
    beta = grab(r"common-equity beta is {N}", text)
    rn = grab(r"nominal market return rn is {N} percent", text)
    pi = grab(r"inflation pi is {N} percent", text)
    rf = grab(r"risk-free rate rf is {N} percent", text)
    ka = grab(r"\bka={N} percent", text)
    kb = grab(r"\bkb={N} percent", text)
    t = grab(r"tax rate T is {N} percent", text)
    # Exact Fisher conversion of the nominal market return to a real return (percent units).
    rm = 100 * ((1 + rn / 100) / (1 + pi / 100) - 1)
    ke = rf + beta * (rm - rf)
    d = da + db
    kd = (da * ka + db * kb) / d
    v = e + d
    w_e = e / v
    w_d = d / v
    wacc = w_e * ke + w_d * kd * (1 - t / 100)
    return {
        "final": wacc,
        "slots": {
            "real_market_return_percent": rm,
            "capm_real_equity_cost_percent": ke,
            "weighted_real_debt_cost_percent": kd,
        },
    }
