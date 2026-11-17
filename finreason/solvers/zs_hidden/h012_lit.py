"""h012 -- concentrated single-transfer whale check (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h012"


def solve(text: str, q: dict) -> dict:
    # "A wallet makes a current transfer of X USD after prior transfers of A USD and B USD."
    current = grab(r"current transfer of {N} USD", text)
    prior_1 = grab(r"prior transfers of {N} USD and {N} USD", text, 1)
    prior_2 = grab(r"prior transfers of {N} USD and {N} USD", text, 2)

    # "Its rolling-window whale threshold is T USD."
    rolling_threshold = grab(r"rolling-window whale threshold is {N} USD", text)

    # "... this threshold is reduced by haircut ratio h, so the single-transfer threshold
    #  is the rolling threshold times (1-single-threshold haircut ratio)."
    haircut = grab(r"reduced by haircut ratio {N}", text)
    retained_fraction = 1 - haircut
    single_threshold = rolling_threshold * retained_fraction

    # "The wallet's total activity over the monitoring horizon, including all three transfers, is V USD."
    total_activity = grab(r"including all three transfers, is {N} USD", text)

    # "Compute current-transfer concentration as current transfer divided by total activity."
    concentration = current / total_activity

    # "If it is at least c, including exact equality, report the current transfer's excess over the
    #  haircut-adjusted single-transfer threshold; otherwise report the three-transfer total's excess
    #  over the unadjusted rolling threshold."
    cutoff = grab(r"If it is at least {N}", text)
    if concentration >= cutoff:
        final = current - single_threshold
    else:
        three_transfer_total = current + prior_1 + prior_2
        final = three_transfer_total - rolling_threshold

    return {
        "final": Fraction(final),
        "slots": {"single_threshold_retention_checkpoint": Fraction(retained_fraction)},
    }
