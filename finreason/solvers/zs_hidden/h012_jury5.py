"""h012 -- whale-transfer excess with a concentration-selected threshold (juror #5).

Rules encoded from the text:
  * single-transfer threshold = rolling threshold * (1 - haircut ratio)
  * concentration = current transfer / total activity over the monitoring horizon
    (the stated total, NOT the sum of the three transfers)
  * if concentration >= cutoff (non-strict), final = current - single threshold
    else final = (current + prior1 + prior2) - rolling threshold
  * slot = retained fraction = 1 - haircut (unrounded; framework rounds to 6 dp)
"""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h012"


def solve(text: str, q: dict) -> dict:
    current = grab(r"current transfer of {N} USD", text)
    prior1 = grab(r"prior transfers of {N} USD", text)
    prior2 = grab(r"prior transfers of (?:{N}) USD and {N} USD", text, group=2)
    rolling = grab(r"whale threshold is {N} USD", text)
    haircut = grab(r"reduced by haircut ratio {N}", text)
    total_activity = grab(r"including all three transfers, is {N} USD", text)
    cutoff = grab(r"If it is at least {N}", text)

    retained = Fraction(1) - haircut
    single_threshold = rolling * retained
    concentration = current / total_activity

    if concentration >= cutoff:
        final = current - single_threshold
    else:
        three_total = current + prior1 + prior2
        final = three_total - rolling

    return {
        "final": final,
        "slots": {"single_threshold_retention_checkpoint": retained},
    }
