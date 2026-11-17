from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.liqratio.liquidity_minimum_quick_ratio.advanced.v1"


def solve(text: str, q: dict) -> dict:
    cash = grab(r"cash {N} USD", text)
    ms = grab(r"marketable securities {N} USD", text)
    ar = grab(r"accounts receivable {N} USD", text)
    inv = grab(r"inventory {N} USD", text)
    prepaid = grab(r"prepaid expenses {N} USD", text)
    cl = grab(r"Current liabilities are {N} USD", text)
    min_ratio = grab(r"minimum quick ratio is {N}", text)

    total_ca = cash + ms + ar + inv + prepaid
    quick = cash + ms + ar
    current_ratio = total_ca / cl
    quick_ratio = quick / cl
    required = min_ratio * cl
    needed = required - quick
    if needed < 0:
        needed = Fraction(0)
    return {
        "final": needed,
        "slots": {"trace_1": current_ratio, "trace_2": quick_ratio, "trace_3": required},
    }
