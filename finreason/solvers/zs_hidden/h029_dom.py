# MODEL (rolling whale-transfer threshold, required next transfer)
#
# Inputs
#   a, b   : the two prior transfers in the current monitoring window (USD)
#   T      : base rolling whale threshold (USD)
#   r      : risk-adjustment ratio, the threshold is "increased by" r
#   E      : the required excess of the rolling total over the adjusted threshold (USD)
#
# Economic model
#   factor      = 1 + r                       (multiplicative risk-adjustment factor, a "multiple")
#                                             "increased by ratio r" => multiply by (1 + r), not by r.
#   adjusted    = T * factor                  (adjusted rolling whale threshold, USD)
#   rolling     = a + b + x                   (rolling total once next transfer x is added)
#   Requirement : rolling = adjusted + E      ("exceed the adjusted threshold by exactly E")
#   => x = T * (1 + r) + E - a - b
#
# Conventions / overrides: none. All arithmetic exact (Fraction). Final answer is the
# UNROUNDED x (framework rounds half-up to 2 dp); checkpoint is the UNROUNDED factor
# (framework rounds half-up to 6 dp). No negativity floor: the text asks for the amount that
# makes the total exceed by exactly E, so x is returned as computed.
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h029"


def solve(text: str, q: dict) -> dict:
    a, b = grab_all(r"two prior transfers of {N} USD and {N} USD", text)
    base = grab(r"base rolling whale threshold is {N} USD", text)
    r = grab(r"risk-adjustment ratio {N}", text)
    excess = grab(r"exceed the adjusted threshold by exactly {N} USD", text)

    factor = 1 + r
    adjusted = base * factor
    x = adjusted + excess - a - b
    return {
        "final": x,
        "slots": {"threshold_adjustment_factor_checkpoint": factor},
    }
