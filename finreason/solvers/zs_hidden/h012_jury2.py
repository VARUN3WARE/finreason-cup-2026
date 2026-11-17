from fractions import Fraction

from finreason.nums import grab, grab_all, F

TEMPLATE_ID = "h012"


def solve(text: str, q: dict) -> dict:
    current, prior1, prior2 = grab_all(
        r"current transfer of {N} USD after prior transfers of {N} USD and {N} USD", text
    )
    rolling = grab(r"rolling-window whale threshold is {N} USD", text)
    haircut = grab(r"reduced by haircut ratio {N}", text)
    total_activity = grab(r"including all three transfers, is {N} USD", text)
    cutoff = grab(r"If it is at least {N}", text)

    # Single-transfer threshold = rolling threshold * (1 - haircut), exact.
    retained = 1 - haircut
    single_threshold = rolling * retained

    # Concentration uses the stated total activity over the monitoring horizon.
    concentration = current / total_activity

    if concentration >= cutoff:  # "at least ... including exact equality"
        final = current - single_threshold
    else:
        # "three-transfer total" = sum of the current and two prior transfers.
        three_total = current + prior1 + prior2
        final = three_total - rolling

    return {
        "final": final,
        "slots": {"single_threshold_retention_checkpoint": retained},
    }
