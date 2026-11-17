from fractions import Fraction

from finreason.nums import grab, real_pow

TEMPLATE_ID = "fp.personal_finance.saveretire.inflation_adjustment.intermediate.v1"


def solve(text: str, q: dict) -> dict:
    spending = grab(r"Current annual spending in USD per year (?:is|are) {N}", text)
    ratio = grab(r"Inflation ratio per period (?:is|are) {N}", text)
    periods = grab(r"period count (?:is|are) {N}", text)
    factor = 1 + ratio
    # real_pow is exact (Fraction ** int) for integer exponents.
    multiple = real_pow(factor, periods)
    return {
        "final": spending * multiple,
        "slots": {"inflation_factor": factor, "inflation_multiple": multiple},
    }
