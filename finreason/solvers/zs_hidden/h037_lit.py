"""h037 -- minimum aggregate coupon cash meeting a target holding-period return.

Literal transcription of the question text, sentence by sentence.
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h037"


def solve(text: str, q: dict) -> dict:
    # S1: "A bond has quoted clean price P and will pay redemption cash R over the planned holding period."
    clean_price = grab(r"quoted clean price {N}", text)
    redemption_cash = grab(r"redemption cash {N}", text)

    # S2: "The investor also pays settlement cost S, defined as all acquisition cash beyond the clean
    #      quote, including accrued interest and fees ...; do not add those amounts again."
    settlement_cost = grab(r"settlement cost {N}", text)

    # S3: "Define total acquisition outlay as clean price plus settlement cost"
    total_acquisition_outlay = clean_price + settlement_cost
    #     "and holding-period return as (aggregate coupon cash plus redemption cash minus total
    #      acquisition outlay) divided by total acquisition outlay."
    def holding_period_return(aggregate_coupon_cash: Fraction) -> Fraction:
        return (aggregate_coupon_cash + redemption_cash - total_acquisition_outlay) / total_acquisition_outlay

    # S4: "Determine the minimum aggregate coupon cash that exactly meets target return ratio T"
    target_return = grab(r"target return ratio {N}", text)
    # HPR(C) = T  <=>  C = T * outlay + outlay - redemption  (HPR is increasing in C, so this is the minimum)
    aggregate_coupon_cash = target_return * total_acquisition_outlay + total_acquisition_outlay - redemption_cash
    assert holding_period_return(aggregate_coupon_cash) == target_return

    return {
        "final": aggregate_coupon_cash,
        "slots": {"acquisition_outlay_checkpoint": total_acquisition_outlay},
    }
