"""h075: initial principal needed to reach a target given a later contribution.

Target T after N annual periods at rate r; a later contribution C is deposited at a
boundary from which exactly M whole periods remain (so it compounds for M periods).
    growth factor on contribution g = (1+r)^M
    P = (T - C*g) / (1+r)^N
No floor at zero is stated, so the exact (possibly negative) value is returned.
"""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h075"


def solve(text: str, q: dict) -> dict:
    target = grab(r"must reach {N} USD", text)
    n = grab(r"after {N} whole annual compounding periods", text)
    r = grab(r"annual rate ratio {N}", text)
    contrib = grab(r"later contribution of {N} USD", text)
    m = grab(r"exactly {N} whole periods remain", text)
    if n.denominator != 1 or m.denominator != 1:
        raise ValueError("non-integer period count")
    g = (1 + r) ** int(m)
    principal = (target - contrib * g) / (1 + r) ** int(n)
    return {"final": principal, "slots": {"later_contribution_growth_checkpoint": g}}
