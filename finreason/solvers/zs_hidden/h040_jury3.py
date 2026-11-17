"""h040 -- token burn then emission under a market-cap ceiling (juror 3).

Reading:
  * supply after the burn S1 = outstanding - burn  (the supply the post-burn price applies to,
    i.e. the "current supply" at the expected price);
  * benchmark market cap = S1 * price; multiple m = (S1 * price) / ceiling   (checkpoint);
  * ceiling-compatible total supply = S1 / m  (== ceiling / price);
  * max additional units = total supply - S1, floored at 0 (cannot emit a negative number);
  * the final value is rounded half-up to a whole token by the framework (unrounded here).
"""
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h040"


def solve(text: str, q: dict) -> dict:
    outstanding = grab(r"has {N} units outstanding", text)
    burn = grab(r"will burn {N} units", text)
    price = grab(r"trade at {N} USD per unit", text)
    ceiling = grab(r"must not exceed {N} USD", text)

    post_burn = outstanding - burn
    benchmark_cap = post_burn * price
    multiple = benchmark_cap / ceiling
    if multiple == 0:
        # degenerate: nothing outstanding, so the supply cap is ceiling / price directly
        total_supply = ceiling / price
    else:
        total_supply = post_burn / multiple
    additional = total_supply - post_burn
    if additional < 0:
        additional = Fraction(0)

    return {
        "final": additional,
        "slots": {"ceiling_utilization_checkpoint": multiple},
    }
