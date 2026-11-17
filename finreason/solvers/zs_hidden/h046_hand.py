"""h046: three-year retirement bridge -- growing withdrawals leaving a required reserve.

Balance path (rate r, withdrawal growth g, opening capital P, reserve R):
    B1 = P(1+r) - W
    B2 = B1(1+r) - W(1+g)
    B3 = B2(1+r) - W(1+g)^2 = R
=> W = (P(1+r)^3 - R) / ((1+r)^2 + (1+g)(1+r) + (1+g)^2)
Checkpoint: gross two-year value of the opening capital before withdrawals = P(1+r)^2.
"""

from fractions import Fraction

from finreason.nums import grab, NUMBER

import re

TEMPLATE_ID = "h046"


def _rate(pattern: str, text: str) -> Fraction:
    """Rate given as a decimal (0.04) or as a percent (4 percent / 4%)."""
    rx = pattern.replace("{N}", f"({NUMBER})\\s*(percent|%)?")
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    v = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        v /= 100
    return v


def solve(text: str, q: dict) -> dict:
    P = grab(r"bridge with (?:USD\s*|\$)?{N}", text)
    r = _rate(r"earns {N}", text)
    g = _rate(r"W times one plus {N}", text)
    R = grab(r"third withdrawal, (?:USD\s*|\$)?{N}\s+must remain", text)

    a = 1 + r
    b = 1 + g
    W = (P * a ** 3 - R) / (a ** 2 + b * a + b ** 2)

    # sanity: the reserve equality holds exactly with the unrounded W
    bal = P * a - W
    bal = bal * a - W * b
    bal = bal * a - W * b ** 2
    assert bal == R

    return {
        "final": W,
        "slots": {"two_year_gross_capital_checkpoint": P * a ** 2},
    }
