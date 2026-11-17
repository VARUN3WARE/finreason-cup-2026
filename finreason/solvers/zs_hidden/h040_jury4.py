"""h040 -- token burn then emission under a market-cap ceiling.

Reading used:
  * "current supply" at the moment of emission is the post-burn supply (the price quoted is the
    post-burn price, and the emission happens after the burn), so
        S_post   = outstanding - burn
        benchmark market cap = S_post * price
        multiple m = benchmark market cap / ceiling          (checkpoint, a plain multiple)
  * ceiling-compatible total supply = S_post / m  (== ceiling / price)
  * max additional units = total supply - S_post, floored at 0 (units cannot be negative: if the
    post-burn supply already breaches the ceiling, nothing may be emitted).
"""
from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h040"


def solve(text: str, q: dict) -> dict:
    outstanding = grab(r"has\s+{N}\s+units\s+outstanding", text)
    burn = grab(r"will\s+burn\s+{N}\s+units", text)
    price = grab(r"trade\s+at\s+{N}\s+USD\s+per\s+unit", text)
    ceiling = grab(r"must\s+not\s+exceed\s+{N}\s+USD", text)

    post_burn = outstanding - burn
    bench_cap = post_burn * price
    multiple = bench_cap / ceiling
    total_supply = post_burn / multiple
    additional = total_supply - post_burn
    if additional < 0:
        additional = Fraction(0)

    return {
        "final": additional,
        "slots": {"ceiling_utilization_checkpoint": multiple},
    }
