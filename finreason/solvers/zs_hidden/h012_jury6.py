from fractions import Fraction
from finreason.nums import grab, grab_all

TEMPLATE_ID = "h012"


def solve(text: str, q: dict) -> dict:
    current = grab(r"current transfer of {N} USD", text)
    priors = grab_all(r"prior transfers of {N} USD and {N} USD", text)
    rolling = grab(r"whale threshold is {N} USD", text)
    haircut = grab(r"haircut ratio {N}", text)
    total_activity = grab(
        r"total activity over the monitoring horizon, including all three transfers, is {N} USD", text
    )
    cutoff = grab(r"If it is at least {N}", text)

    # Retained fraction after the single-transfer haircut (the checkpoint, a plain ratio).
    retained = Fraction(1) - haircut
    # Haircut-adjusted single-transfer threshold = rolling threshold x (1 - haircut).
    single_threshold = rolling * retained

    # Concentration uses the stated total activity (which may exceed the three-transfer sum).
    concentration = current / total_activity

    if concentration >= cutoff:  # "at least", exact equality included
        excess = current - single_threshold
    else:
        # "three-transfer total" = current + both prior transfers, vs the unadjusted rolling threshold.
        three_total = current + sum(priors, Fraction(0))
        excess = three_total - rolling

    return {"final": excess, "slots": {"single_threshold_retention_checkpoint": retained}}
