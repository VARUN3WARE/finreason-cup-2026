"""h040 -- token burn, post-burn price, market-cap ceiling -> maximum additional emission.

Reviewer 2 (upholds adjA): "current supply" = units outstanding now (pre-burn); no zero floor (none stated).
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h040"


def solve(text: str, q: dict) -> dict:
    # "A token has {N} units outstanding and will burn {N} units."
    current_supply = grab(r"has {N} units outstanding", text)
    burn_units = grab(r"will burn {N} units", text)
    post_burn_supply = current_supply - burn_units

    # "After the burn, the token is expected to trade at {N} USD per unit, and this price is
    #  assumed to remain unchanged when additional units are emitted."
    expected_price = grab(r"expected to trade at {N} USD per unit", text)

    # "If total market capitalization must not exceed {N} USD, ..."
    ceiling = grab(r"must not exceed {N} USD", text)

    # "... first compute the market cap of the current supply at that expected price,"
    benchmark_market_cap = current_supply * expected_price

    # "express it as a multiple of the ceiling,"
    ceiling_multiple = benchmark_market_cap / ceiling

    # "and use that multiple to recover the ceiling-compatible total supply."
    # (current supply scaled down by the multiple == ceiling / price)
    ceiling_compatible_total_supply = current_supply / ceiling_multiple

    # "What is the maximum number of additional token units that may be emitted after the burn?"
    # Total supply after emission = post-burn supply + additional units <= ceiling-compatible supply.
    # No floor at zero is stated in the text, so the exact difference is returned; the framework
    # applies half-up rounding to the nearest whole token.
    max_additional_units = ceiling_compatible_total_supply - post_burn_supply

    return {
        "final": Fraction(max_additional_units),
        "slots": {"ceiling_utilization_checkpoint": Fraction(ceiling_multiple)},
    }
