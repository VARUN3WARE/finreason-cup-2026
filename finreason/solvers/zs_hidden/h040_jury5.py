"""h040 -- token burn, then maximum emission under a market-cap ceiling.

Reading of the text (juror 5):
  * units outstanding N, burn B  ->  post-burn supply S = N - B
  * expected post-burn price P (assumed unchanged while emitting)
  * ceiling C on *total* market cap
  * "market cap of the current supply at that expected price":  MC = S * P
    ("current" = the supply that exists when the price applies and before the
    additional units, i.e. post-burn, pre-emission; it is contrasted with the
    "total" supply after emission)
  * checkpoint: MC expressed as a multiple of the ceiling  m = MC / C
  * ceiling-compatible total supply  T = S / m  ( = C / P )
  * answer: additional units emittable after the burn = T - S, exact, framework
    rounds half-up to a whole token.  No floor/clamp is stated in the text, so a
    negative headroom (ceiling already breached) is reported as is.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h040"


def solve(text: str, q: dict) -> dict:
    outstanding = grab(r"has {N} units outstanding", text)
    burn = grab(r"will burn {N} units", text)
    price = grab(r"trade at {N} USD per unit", text)
    ceiling = grab(r"must not exceed {N} USD", text)

    post_burn_supply = outstanding - burn                      # units after the burn
    market_cap = post_burn_supply * price                      # USD, current (post-burn) supply
    multiple = market_cap / ceiling                            # multiple of the ceiling
    total_supply = post_burn_supply / multiple                 # ceiling-compatible total supply
    additional = total_supply - post_burn_supply               # units that may still be emitted

    return {
        "final": Fraction(additional),
        "slots": {"ceiling_utilization_checkpoint": Fraction(multiple)},
    }
