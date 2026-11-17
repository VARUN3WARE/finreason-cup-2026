# FINANCE MODEL (h040) -- token burn / market-cap ceiling / emission headroom
#
# Given:
#   S  = units outstanding now
#   B  = units burned (burn happens first)
#   p  = expected USD price per unit after the burn; price is held constant when new units are emitted
#   C  = market-cap ceiling in USD (total market cap must not exceed C)
#
# Model:
#   current (post-burn) supply   N = S - B           (the supply that exists when emission starts and
#                                                      to which the expected price applies)
#   benchmark market cap         M = N * p           (market cap of the current supply at the expected price)
#   ceiling utilisation multiple m = M / C           <- checkpoint 1 (multiple of the ceiling)
#   ceiling-compatible total supply  T = N / m = C / p   (supply at which cap == ceiling, price constant)
#   headroom (additional units)  A = T - N
#   The number of units that may be emitted cannot be negative: if the ceiling is already exceeded
#   (m > 1) nothing may be emitted, so A = max(0, T - N).
#   Final answer = A rounded half-up to a whole token (framework applies rounding).
#
# Overrides / interpretation notes:
#   * "current supply" is taken as the post-burn supply (price quoted is the post-burn price). The final
#     answer is independent of this choice (T = C/p either way); only the checkpoint multiple depends on it.
#   * Max(0, .) floor on the headroom: "maximum number of units that may be emitted" cannot be negative.

from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h040"


def solve(text: str, q: dict) -> dict:
    supply = grab(r"has {N} units outstanding", text)
    burn = grab(r"burn {N} units", text)
    price = grab(r"trade at {N} USD per unit", text)
    ceiling = grab(r"must not exceed {N} USD", text)

    current = supply - burn
    bench_cap = current * price
    multiple = bench_cap / ceiling
    if multiple == 0:
        raise ValueError("zero benchmark market cap")
    max_total_supply = current / multiple  # == ceiling / price
    headroom = max_total_supply - current
    if headroom < 0:
        headroom = Fraction(0)

    return {
        "final": headroom,
        "slots": {"ceiling_utilization_checkpoint": multiple},
    }
