from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h012"


def solve(text: str, q: dict) -> dict:
    cur, prior1, prior2 = grab_all(
        r"current transfer of {N} USD after prior transfers of {N} USD and {N} USD", text
    )
    rolling = grab(r"rolling-window whale threshold is {N} USD", text)
    haircut = grab(r"haircut ratio {N}", text)
    total_activity = grab(r"including all three transfers, is {N} USD", text)
    conc_cut = grab(r"If it is at least {N}", text)

    # Retained fraction used for the concentrated single-transfer threshold (exact, unrounded).
    retention = 1 - haircut
    single_threshold = rolling * retention

    # Concentration = current transfer / total activity over the monitoring horizon
    # (the stated total activity, not the sum of the three transfers). Non-strict comparison.
    concentration = cur / total_activity

    if concentration >= conc_cut:
        excess = cur - single_threshold
    else:
        # "three-transfer total" = current + the two prior transfers (distinct from total activity)
        three_total = cur + prior1 + prior2
        excess = three_total - rolling

    return {
        "final": excess,
        "slots": {"single_threshold_retention_checkpoint": retention},
    }
