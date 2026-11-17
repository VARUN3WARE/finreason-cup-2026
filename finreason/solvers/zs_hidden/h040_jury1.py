from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h040"


def solve(text: str, q: dict) -> dict:
    outstanding = grab(r"has {N} (?:token )?units outstanding", text)
    burn = grab(r"will burn {N} (?:token )?units", text)
    price = grab(r"expected to trade at {N} USD per unit", text)
    ceiling = grab(r"must not exceed {N} USD", text)

    # "current supply" = units outstanding now (the burn is still in the future),
    # valued at the expected post-burn price -> benchmark market cap.
    benchmark_cap = outstanding * price
    multiple = benchmark_cap / ceiling          # checkpoint: multiple of the ceiling
    ceiling_supply = outstanding / multiple     # recovered ceiling-compatible total supply (= ceiling / price)

    post_burn = outstanding - burn
    additional = ceiling_supply - post_burn     # unclamped; half-up rounding applied by framework
    return {
        "final": additional,
        "slots": {"ceiling_utilization_checkpoint": multiple},
    }
