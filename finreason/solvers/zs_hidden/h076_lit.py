"""h076 -- signed Tier 1 adjustment x satisfying a combined capital ratio and a leverage ratio.

Literal transcription of the question text, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h076"


def solve(text: str, q: dict) -> dict:
    # "A bank has eligible Tier 1 capital T1 and eligible Tier 2 capital T2,
    #  risk-weighted assets RWA, and total exposure E, all in USD millions."
    tier1 = grab(r"eligible Tier 1 capital {N}", text)
    tier2 = grab(r"eligible Tier 2 capital {N}", text)
    risk_weighted_assets = grab(r"risk-weighted assets {N}", text)
    total_exposure = grab(r"total exposure {N}", text)

    # "The scenario supplies minimum capital ratio m, capital buffer ratio b,
    #  and minimum leverage ratio l as decimal ratios."
    minimum_capital_ratio = grab(r"minimum capital ratio {N}", text)
    capital_buffer_ratio = grab(r"capital buffer ratio {N}", text)
    minimum_leverage_ratio = grab(r"minimum leverage ratio {N}", text)

    # "One signed Tier 1 adjustment x changes both Tier 1 capital and total
    #  eligible capital by x while leaving Tier 2 capital, RWA, and exposure fixed."
    # "Add the minimum capital ratio and buffer ratio."
    combined_ratio = minimum_capital_ratio + capital_buffer_ratio

    # "The capital constraint requires x to be at least
    #  combined_ratio*risk_weighted_assets-(Tier1+Tier2)"
    capital_gap = combined_ratio * risk_weighted_assets - (tier1 + tier2)

    # "while the leverage constraint requires x to be at least
    #  minimum_leverage_ratio*total_exposure-Tier1."
    leverage_gap = minimum_leverage_ratio * total_exposure - tier1

    # "Return the larger gap."  (signed: positive = issuance, negative = permitted withdrawal)
    x = max(capital_gap, leverage_gap)

    return {
        "final": Fraction(x),
        "slots": {
            "combined_capital_requirement_ratio_checkpoint": Fraction(combined_ratio),
        },
    }
