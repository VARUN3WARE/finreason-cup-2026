"""h041: two-period loan roll-forward; solve for the second-period payment that hits a target balance.

Balance after period 1:  B1 = P0 * (1 + r) - pay1
Payment in period 2:     pay2 = B1 * (1 + r) - target   (interest applied before end-of-period payment)
"""

from fractions import Fraction
import re

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h041"


def _rate(text: str) -> Fraction:
    m = re.search(r"rate of\s+(" + NUMBER + r")\s*(percent|%)?", text)
    if m is None:
        raise ValueError("rate not found")
    v = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        v /= 100
    return v


def solve(text: str, q: dict) -> dict:
    p0 = grab(r"outstanding principal of\s+(?:USD\s*|\$)?{N}", text)
    r = _rate(text)
    pay1 = grab(r"pays\s+(?:USD\s*|\$)?{N}\s+at the end of the first period", text)
    target = grab(r"leaves a balance of\s+(?:USD\s*|\$)?{N}", text)

    b1 = p0 * (1 + r) - pay1
    pay2 = b1 * (1 + r) - target

    return {"final": pay2, "slots": {"first_payment_balance_checkpoint": b1}}
