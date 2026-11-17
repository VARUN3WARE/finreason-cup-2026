"""h040: token emission headroom under a market-cap ceiling (hand-solved first).

Chain (exact):
  current supply S (units outstanding now), burn B, post-burn supply S - B
  expected post-burn price P (unchanged by emission), market-cap ceiling C
  benchmark market cap of the current supply at P : S * P
  ceiling_utilization_checkpoint = S * P / C          (multiple of the ceiling)
  ceiling-compatible total supply = S / multiple      (= C / P)
  max additional units after the burn = total supply - (S - B)
Final is returned unrounded; the framework rounds half up to a whole token.
No floor at zero is stated, so a breached ceiling yields a negative headroom.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h040"


def solve(text: str, q: dict) -> dict:
    outstanding = grab(r"has {N} units outstanding", text)
    burn = grab(r"will burn {N} units", text)
    price = grab(r"expected to trade at {N} USD per unit", text)
    ceiling = grab(r"must not exceed {N} USD", text)

    post_burn = outstanding - burn

    benchmark_cap = outstanding * price            # current supply at the expected price
    multiple = benchmark_cap / ceiling             # as a multiple of the ceiling
    total_supply = outstanding / multiple          # ceiling-compatible total supply (= C / P)

    additional = total_supply - post_burn

    return {
        "final": Fraction(additional),
        "slots": {"ceiling_utilization_checkpoint": Fraction(multiple)},
    }
