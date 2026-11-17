"""h100 -- Modified Dietz ROI with an interim contribution and a terminal distribution.

Literal transcription of the question, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h100"


def solve(text: str, q: dict) -> dict:
    # "An investment account begins a measurement period at value {BMV}."
    bmv = grab(r"begins a measurement period at value {N}", text)

    # "A contribution of {C} is added after {t} of the period has elapsed."
    contribution = grab(r"A contribution of {N} is added", text)
    elapsed = grab(r"is added after {N} of the period has elapsed", text)

    # "At period end, the post-distribution account value is {EMV} and a terminal
    #  cash distribution of {D} is paid at that same time; the ending value
    #  excludes that distribution."
    emv = grab(r"post-distribution account value is {N}", text)
    distribution = grab(r"terminal cash distribution of {N}", text)

    # "There are no other external cash flows."
    # Net external flow (inflows positive, outflows negative).
    net_flow = contribution - distribution

    # "Under the standard Modified Dietz convention, weight the contribution by
    #  the fraction of the period remaining and give the terminal distribution
    #  zero denominator weight."
    w_contribution = Fraction(1) - elapsed
    w_distribution = Fraction(0)
    weighted_contribution = contribution * w_contribution
    weighted_flows = weighted_contribution + (-distribution) * w_distribution

    # Modified Dietz: gain = EMV - BMV - net flows; base = BMV + sum(w_i * CF_i).
    gain = emv - bmv - net_flow
    capital_base = bmv + weighted_flows

    # "What is the period's Modified Dietz ROI as a percentage?"
    roi_pct = gain / capital_base * 100

    return {
        "final": roi_pct,
        "slots": {"weighted_contribution_checkpoint": weighted_contribution},
    }
