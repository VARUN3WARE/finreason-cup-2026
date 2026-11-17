from fractions import Fraction
import re
from finreason.nums import grab, F, NUMBER

TEMPLATE_ID = "h022"


def solve(text: str, q: dict) -> dict:
    # Pre-deal common shares, expressed as aggregate value at the single fixed contractual price.
    predeal = grab(r"predeal common shares have aggregate reference equity value {N}", text)
    base = grab(r"Upfront base consideration is {N}", text)
    # Cash share of the base: either a fraction ("0.2 of that base") or a percent ("20 percent of that base").
    m = re.search(rf"({NUMBER})\s*(percent|%)?\s*of that base is paid in cash", text)
    cash_frac = F(m.group(1))
    if m.group(2):
        cash_frac /= 100
    upfront_stock = base * (1 - cash_frac)
    earnout = grab(r"earnout with settlement value {N}", text)

    # Same unchanged price for all issuances -> ownership is value-weighted.
    seller_value = upfront_stock + earnout
    total_value = predeal + seller_value
    ownership_pct = seller_value / total_value * 100
    return {
        "final": ownership_pct,
        "slots": {"upfront_stock_consideration_checkpoint": upfront_stock},
    }
