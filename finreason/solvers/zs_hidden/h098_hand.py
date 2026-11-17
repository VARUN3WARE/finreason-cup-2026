"""h098: maximum risky-asset weight under a stress floor and a policy cap.

Stressed value = V - w * V * L  >=  Floor   =>   w <= (V - Floor) / (V * L)
Max permitted weight = min(stress-implied weight, policy cap)   (also bounded to [0, 1]).
Checkpoint: loss budget = V - Floor (allowable dollar loss under the floor).
"""
from fractions import Fraction
import re

from finreason.nums import grab, F, NUMBER

TEMPLATE_ID = "h098"


def _frac_or_pct(pattern: str, text: str) -> Fraction:
    """Parse a number given either as a plain fraction (0.3) or as a percentage (30 percent / 30%)."""
    rx = pattern.replace("{N}", f"({NUMBER})\\s*(percent|%)?")
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    v = F(m.group(1))
    if m.group(2):
        v = v / 100
    return v


def solve(text: str, q: dict) -> dict:
    value = grab(r"portfolio worth (?:USD\s*|\$)?{N}", text)
    floor = grab(r"at or above (?:USD\s*|\$)?{N}", text)
    loss = _frac_or_pct(r"loses {N}", text)
    cap = _frac_or_pct(r"weight at {N}", text)

    loss_budget = value - floor
    stress_w = loss_budget / (value * loss)
    w = min(stress_w, cap)
    if w > 1:
        w = Fraction(1)
    if w < 0:
        w = Fraction(0)

    return {
        "final": w * 100,
        "slots": {"loss_budget_checkpoint": loss_budget},
    }
