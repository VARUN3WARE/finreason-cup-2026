from fractions import Fraction

from finreason.nums import grab, grab_all, F

TEMPLATE_ID = "h012"


def solve(text: str, q: dict) -> dict:
    # Inputs, each pulled from its own sentence.
    current = grab(r"current transfer of {N} USD", text)
    prior1, prior2 = grab_all(r"prior transfers of {N} USD and {N} USD", text)
    rolling = grab(r"whale threshold is {N} USD", text)
    haircut = grab(r"haircut ratio {N},", text)
    horizon_total = grab(r"including all three transfers, is {N} USD", text)
    conc_cut = grab(r"If it is at least {N}", text)

    # Retained fraction (checkpoint) and haircut-adjusted single-transfer threshold, exact.
    retention = 1 - haircut
    single_threshold = rolling * retention

    # Concentration = current transfer / total activity over the monitoring horizon
    # (the horizon total is a separate quantity from the three-transfer sum).
    concentration = current / horizon_total

    if concentration >= conc_cut:  # non-strict: equality takes the concentrated branch
        excess = current - single_threshold
    else:
        three_total = current + prior1 + prior2  # the three named transfers only
        excess = three_total - rolling

    return {
        "final": excess,
        "slots": {"single_threshold_retention_checkpoint": retention},
    }
