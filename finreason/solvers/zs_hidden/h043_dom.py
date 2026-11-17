# FINANCE MODEL (inverse WACC)
#
# Capital structure weights use market (stated) values:
#     V = E + D,   wE = E / V,   wD = D / V
# Standard WACC with a debt tax shield:
#     WACC = wE * Re + wD * Rd * (1 - t)
# Inputs:
#   - E (equity value) and D (debt value) are plain amounts; only their ratio / weights matter.
#   - Re (cost of equity) is given as a percentage number (12 means 12%).
#   - t is given explicitly as a RATIO (0.28 means 28%); NOT divided by 100.
#   - WACC ceiling is given as a percentage number (10 means 10%).
# Question: the maximum pre-tax cost of debt Rd such that WACC <= ceiling.
#   WACC is strictly increasing in Rd (D > 0, t < 1), so the maximum feasible Rd is where
#   WACC == ceiling exactly:
#       Rd = (ceiling - wE * Re) / (wD * (1 - t))
#   Working in percent units throughout keeps Rd in percent directly.
#   Equivalent form with the debt-to-equity ratio  d = D / E :
#       wE = 1 / (1 + d),  wD = d / (1 + d)
#       Rd = (ceiling * (1 + d) - Re) / (d * (1 - t))
# Checkpoint 1: debt_to_equity = D / E (plain ratio), the quantity used by the inverse WACC.
# Final: Rd in percent, unrounded exact Fraction (framework rounds half-up to 2 dp).
# Overrides: tax rate is a ratio (no /100); cost of equity and ceiling are percent numbers.

from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h043"


def solve(text: str, q: dict) -> dict:
    E = grab(r"equity value {N}", text)
    D = grab(r"debt value {N}", text)
    re_pct = grab(r"cost of equity percentage {N}", text)
    t = grab(r"corporate tax rate ratio {N}", text)
    ceiling_pct = grab(r"WACC ceiling {N}", text)

    d_e = D / E
    wE = E / (E + D)
    wD = D / (E + D)
    rd_pct = (ceiling_pct - wE * re_pct) / (wD * (1 - t))

    return {"final": rd_pct, "slots": {"debt_to_equity_checkpoint": d_e}}
