from fractions import Fraction

from finreason.nums import grab, real_pow

TEMPLATE_ID = "fp.investment_analysis.roi.compound_growth_roi.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    p = grab(r"USD {N} earns", text)
    r = grab(r"compound return of {N} percent", text)
    n = grab(r"percent for {N} year", text)
    base = 1 + r / 100
    if n.denominator == 1:
        mult = base ** int(n)
    else:
        mult = real_pow(base, n)
    ending = p * mult
    profit = ending - p
    roi = profit / p * 100
    return {
        "final": roi,
        "slots": {
            "growth_multiplier_trace": mult,
            "ending_value_trace": ending,
            "investment_profit_trace": profit,
        },
    }
