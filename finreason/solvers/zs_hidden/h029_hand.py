from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h029"


def solve(text: str, q: dict) -> dict:
    t1, t2 = grab_all(r"two prior transfers of {N} USD and {N} USD", text)
    base = grab(r"base rolling whale threshold is {N} USD", text)
    ratio = grab(r"risk-adjustment ratio {N}", text)
    excess = grab(r"exceed the adjusted threshold by exactly {N} USD", text)

    factor = 1 + ratio                     # threshold "increased by" the ratio
    adjusted = base * factor
    target_total = adjusted + excess       # rolling total that exceeds by exactly `excess`
    required = target_total - (t1 + t2)    # exact solution, no floor (text asks for "exactly")

    return {
        "final": Fraction(required),
        "slots": {"threshold_adjustment_factor_checkpoint": Fraction(factor)},
    }
