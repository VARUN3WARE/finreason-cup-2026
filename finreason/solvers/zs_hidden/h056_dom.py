# FINANCE MODEL (h056) -- stressed capital charge with interaction and concentration add-ons
#
# Inputs (all plain ratios unless noted):
#   V   = portfolio value (USD)
#   s1, s2 = factor shock ratios
#   b1, b2 = loss sensitivities paired with s1, s2 respectively
#   k   = interaction coefficient ("product of both shocks and k")
#   c   = concentration ratio
#   E   = external stress loss (USD)
#
# Rates (fractions of portfolio value):
#   linear_1 = s1 * b1 ; linear_2 = s2 * b2          (shock x loss sensitivity = loss rate per factor)
#   joint    = s1 * s2 * k                           (joint interaction loss ratio -> checkpoint)
#   conc     = c ** 2                                (concentration add-on = squared concentration ratio)
#   modeled loss rate = linear_1 + linear_2 + joint + conc
#
# Dollar quantities:
#   modeled loss    = V * modeled loss rate          (USD)
#   capital charge  = max(modeled loss, E)           (final answer, USD, 2 dp half-up)
#
# Conventions / overrides: none beyond the text. Joint effect is multiplicative in the two shocks and k,
# NOT multiplied by the sensitivities. The checkpoint is the joint rate as a ratio (not scaled by V).

import re
from fractions import Fraction

from finreason.nums import grab, grab_all, F  # noqa: F401

TEMPLATE_ID = "h056"


def solve(text: str, q: dict) -> dict:
    V = grab(r"portfolio worth {N}", text)
    s1, s2 = grab_all(r"factor shock ratios {N} and {N}", text)
    b1, b2 = grab_all(r"loss sensitivities {N} and {N}", text)
    k = grab(r"product of both shocks and {N}", text)
    c = grab(r"concentration ratio {N}", text)
    E = grab(r"external stress loss {N}", text)

    linear = s1 * b1 + s2 * b2
    joint = s1 * s2 * k
    conc = c ** 2
    rate = linear + joint + conc
    modeled = V * rate
    capital = modeled if modeled > E else E  # "larger of"; tie yields identical value

    return {"final": capital, "slots": {"joint_ratio_checkpoint": joint}}
