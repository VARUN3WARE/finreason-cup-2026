"""Current ratio = current assets / current liabilities."""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.liqratio.current_ratio_simple.basic.v1"


def solve(text: str, q: dict) -> dict:
    ca = grab(r"current assets (?:of|are|total)\s+(?:USD\s+)?{N}", text)
    cl = grab(r"current liabilities (?:of|are|total)\s+(?:USD\s+)?{N}", text)
    return {"final": Fraction(ca) / cl, "slots": {}}
