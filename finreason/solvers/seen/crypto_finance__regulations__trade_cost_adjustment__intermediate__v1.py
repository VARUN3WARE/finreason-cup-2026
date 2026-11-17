from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.crypto_finance.regulations.trade_cost_adjustment.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"originally costs {N} USD", text)
    multiple = grab(r"total-cost multiple of {N}", text)
    minimum = grab(r"minimum additional charge of {N} USD", text)
    inc = multiple - 1
    calculated = cost * inc
    final = calculated if calculated >= minimum else minimum   # max(calculated, minimum)
    return {
        "final": final,
        "slots": {"increase_multiple_trace": inc, "calculated_cost_trace": calculated},
    }
