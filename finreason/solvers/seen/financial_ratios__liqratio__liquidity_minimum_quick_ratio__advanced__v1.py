"""Minimum additional quick assets to meet a minimum quick ratio (floored at zero).

Current ratio uses all listed current assets (cash, securities, AR, inventory, prepaid).
Quick assets = cash + marketable securities + accounts receivable.
Required = minimum ratio * CL (liabilities unchanged); final = max(0, required - quick).
"""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.liqratio.liquidity_minimum_quick_ratio.advanced.v1"


def solve(text: str, q: dict) -> dict:
    cash = grab(r"\bcash (?:of\s+)?(?:USD\s+)?{N}", text)
    sec = grab(r"marketable securities (?:of\s+)?(?:USD\s+)?{N}", text)
    ar = grab(r"accounts receivable (?:of\s+)?(?:USD\s+)?{N}", text)
    inv = grab(r"inventory (?:of\s+)?(?:USD\s+)?{N}", text)
    pre = grab(r"prepaid expenses (?:of\s+)?(?:USD\s+)?{N}", text)
    cl = grab(r"[Cc]urrent liabilities (?:are|of|total)\s+(?:USD\s+)?{N}", text)
    min_ratio = grab(r"minimum quick ratio (?:is|of)\s+{N}", text)
    total_ca = cash + sec + ar + inv + pre
    quick = Fraction(cash + sec + ar)
    current_ratio = Fraction(total_ca) / cl
    quick_ratio = quick / cl
    required = min_ratio * cl
    additional = required - quick
    if additional < 0:
        additional = Fraction(0)
    return {"final": additional,
            "slots": {"trace_1": current_ratio, "trace_2": quick_ratio, "trace_3": required}}
