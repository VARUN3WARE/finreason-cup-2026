from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h040"


def solve(text: str, q: dict) -> dict:
    outstanding = grab(r"has {N} units outstanding", text)
    burned = grab(r"will burn {N} units", text)
    price = grab(r"trade at {N} USD per unit", text)
    ceiling = grab(r"must not exceed {N} USD", text)

    # Supply at the time the expected (post-burn) price applies.
    supply = outstanding - burned
    market_cap = supply * price
    multiple = market_cap / ceiling              # ceiling utilization
    max_total_supply = supply / multiple         # = ceiling / price
    additional = max_total_supply - supply       # no clamp at zero stated

    return {
        "final": additional,
        "slots": {"ceiling_utilization_checkpoint": multiple},
    }
