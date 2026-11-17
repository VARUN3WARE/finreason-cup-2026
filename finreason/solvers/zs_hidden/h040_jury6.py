"""h040 -- token burn, fixed post-burn price, market-cap ceiling: max additional emission.

Reading of the text (juror 6):
  * outstanding S, burn B  -> post-burn supply S_pb = S - B (the supply in place when the
    expected price applies and when additional units would be emitted).
  * price P is the post-burn price and stays constant through any emission.
  * "market cap of the current supply at that expected price" = S_pb * P  (the supply that is
    current once the burn has happened; this is the real post-burn market cap, which is what a
    "ceiling utilization" measures).  Alternative reading: pre-burn S * P (see interpretation).
  * multiple m = (S_pb * P) / C      -> slot ceiling_utilization_checkpoint (unit "multiple").
  * ceiling-compatible total supply = S_pb / m = C / P   (same under either reading of "current").
  * additional units = C / P - S_pb, reported exact; framework rounds half-up to 0 dp.
    No clamp at zero and no floor: the text asks for exact arithmetic then half-up rounding and
    never states a zero floor.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h040"


def solve(text: str, q: dict) -> dict:
    outstanding = grab(r"has {N} units outstanding", text)
    burn = grab(r"will burn {N} units", text)
    price = grab(r"trade at {N} USD per unit", text)
    ceiling = grab(r"must not exceed {N} USD", text)

    post_burn = outstanding - burn                 # supply after the burn
    current_cap = post_burn * price                # market cap of the current (post-burn) supply
    multiple = current_cap / ceiling               # multiple of the ceiling (utilization)
    total_supply = post_burn / multiple            # ceiling-compatible total supply (= C / P)
    additional = total_supply - post_burn          # max additional units, exact

    return {
        "final": Fraction(additional),
        "slots": {"ceiling_utilization_checkpoint": Fraction(multiple)},
    }
