from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.liqratio.both_ratios.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    ca = grab(r"Current assets are {N} USD", text)
    inv = grab(r"inventory {N} USD", text)
    prepaid = grab(r"prepaid expenses {N} USD", text)
    cl = grab(r"Current liabilities are {N} USD", text)
    current_ratio = ca / cl
    quick_assets = ca - inv - prepaid
    return {
        "final": quick_assets / cl,
        "slots": {"trace_1": current_ratio, "trace_2": quick_assets},
    }
