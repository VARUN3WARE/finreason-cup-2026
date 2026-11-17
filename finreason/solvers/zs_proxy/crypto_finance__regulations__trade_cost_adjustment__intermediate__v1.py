from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.regulations.trade_cost_adjustment.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"originally costs {N} USD", text)
    mult = grab(r"total-cost multiple of {N}", text)
    minimum = grab(r"minimum additional charge of {N} USD", text)
    inc_mult = mult - 1
    calc = inc_mult * cost
    final = max(calc, minimum)
    return {
        "final": final,
        "slots": {"increase_multiple_trace": inc_mult, "calculated_cost_trace": calc},
    }
