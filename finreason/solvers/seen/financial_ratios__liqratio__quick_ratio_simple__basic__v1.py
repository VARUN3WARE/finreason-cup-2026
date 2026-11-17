"""Quick ratio = (current assets - inventory) / current liabilities."""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.liqratio.quick_ratio_simple.basic.v1"


def solve(text: str, q: dict) -> dict:
    ca = grab(r"[Cc]urrent assets (?:are|of|total)\s+(?:USD\s+)?{N}", text)
    inv = grab(r"inventory (?:of\s+)?(?:USD\s+)?{N}", text)
    cl = grab(r"current liabilities (?:are|of|total)\s+(?:USD\s+)?{N}", text)
    quick_assets = ca - inv
    return {"final": Fraction(quick_assets) / cl, "slots": {"trace_1": quick_assets}}
