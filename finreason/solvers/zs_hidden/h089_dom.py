# FINANCE MODEL (h089) -- fictional KYC control-credit policy (scenario-local rules only)
#
# Inputs, all on the same additive risk-point scale:
#   S = source-of-funds risk score
#   J = jurisdiction risk score
#   E = existing verified-control credit
#   C = standard residual-risk ceiling
#   A = additional verified-control credit to be found (A >= 0)
#
# Residual risk = (S + J) - E - A   (existing and additional credit each reduce residual risk one-for-one).
# Requirement: residual risk <= C   (no greater than the ceiling, so equality is acceptable).
#   => A >= S + J - E - C
# Minimum additional credit, with the non-negativity floor:
#   A* = max(0, S + J - E - C)
#
# Checkpoint "combined_risk_checkpoint" (position 1): the combined source-of-funds and
#   jurisdiction risk score = S + J (gross, BEFORE any credit is deducted), dimensionless points.
# Final answer: A* in dimensionless risk-score points (half-up to 2 dp applied by the framework).
#
# Overrides of standard conventions: none. Floor at zero is explicit in the text ("cannot be negative").
# No rounding inside the computation; everything is exact Fraction arithmetic.

from fractions import Fraction

from finreason.nums import grab, after, before, numbers, grab_all, F  # noqa: F401

TEMPLATE_ID = "h089"


def solve(text: str, q: dict) -> dict:
    s = grab(r"source-of-funds risk score {N}", text)
    j = grab(r"jurisdiction risk score {N}", text)
    e = grab(r"existing verified-control credit {N}", text)
    c = grab(r"standard residual-risk ceiling {N}", text)

    combined = s + j
    required = combined - e - c
    if required < 0:
        required = Fraction(0)

    return {"final": required, "slots": {"combined_risk_checkpoint": combined}}
