"""Minimum additional quick assets to reach a target quick ratio (floored at zero).

Quick assets = current assets - inventory - prepaid expenses; required = target * CL
(liabilities unchanged); final = max(0, required - current quick assets).
"""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.liqratio.quick_ratio_target.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    ca = grab(r"[Cc]urrent assets (?:are|of|total)\s+(?:USD\s+)?{N}", text)
    inv = grab(r"inventory (?:of\s+)?(?:USD\s+)?{N}", text)
    pre = grab(r"prepaid expenses (?:of\s+)?(?:USD\s+)?{N}", text)
    cl = grab(r"[Cc]urrent liabilities (?:are|of|total)\s+(?:USD\s+)?{N}", text)
    target = grab(r"target quick ratio (?:is|of)\s+{N}", text)
    quick_assets = Fraction(ca - inv - pre)
    required = target * cl
    additional = required - quick_assets
    if additional < 0:
        additional = Fraction(0)
    return {"final": additional,
            "slots": {"trace_1": quick_assets, "trace_2": required}}
