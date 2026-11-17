"""Quick ratio excluding inventory and prepaid expenses; current ratio as trace."""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.financial_ratios.liqratio.both_ratios.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    ca = grab(r"[Cc]urrent assets (?:are|of|total)\s+(?:USD\s+)?{N}", text)
    inv = grab(r"inventory (?:of\s+)?(?:USD\s+)?{N}", text)
    pre = grab(r"prepaid expenses (?:of\s+)?(?:USD\s+)?{N}", text)
    cl = grab(r"[Cc]urrent liabilities (?:are|of|total)\s+(?:USD\s+)?{N}", text)
    current_ratio = Fraction(ca) / cl
    quick_assets = ca - inv - pre
    quick_ratio = Fraction(quick_assets) / cl
    return {"final": quick_ratio,
            "slots": {"trace_1": current_ratio, "trace_2": quick_assets}}
