from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h012"


def solve(text: str, q: dict) -> dict:
    current = grab(r"current transfer of {N} USD", text)
    p1, p2 = grab_all(r"prior transfers of {N} USD and {N} USD", text)
    rolling = grab(r"whale threshold is {N} USD", text)
    haircut = grab(r"haircut ratio {N}", text)
    total_activity = grab(r"including all three transfers, is {N} USD", text)
    cutoff = grab(r"If it is at least {N}", text)

    retained = 1 - haircut
    single_threshold = rolling * retained
    concentration = current / total_activity
    if concentration >= cutoff:
        final = current - single_threshold
    else:
        final = (current + p1 + p2) - rolling
    return {"final": final, "slots": {"single_threshold_retention_checkpoint": retained}}
