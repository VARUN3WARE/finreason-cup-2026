"""h116: maximum COGS that exactly meets a required operating margin.

Operating income = revenue - COGS - operating expenses, and
operating margin = operating income / revenue.  Exactly meeting the required
margin m (given in percent) means
    revenue - COGS - opex = m * revenue
so the maximum COGS is revenue * (1 - m) - opex (USD millions).
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h116"


def solve(text: str, q: dict) -> dict:
    revenue = grab(r"projected revenue of (?:USD\s*)?{N}", text)
    opex = grab(r"operating expenses of (?:USD\s*)?{N}", text)
    margin_pct = grab(r"required operating margin of {N}", text)

    # Checkpoint 1: required operating margin converted from percent to a ratio.
    margin_ratio = Fraction(margin_pct) / 100

    # Operating income needed to hit the margin exactly, then back out COGS.
    required_operating_income = margin_ratio * revenue
    max_cogs = revenue - opex - required_operating_income

    return {
        "final": max_cogs,
        "slots": {"target_margin_ratio_checkpoint": margin_ratio},
    }
