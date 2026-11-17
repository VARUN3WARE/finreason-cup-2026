# FINANCE MODEL (h032): maximum management fee subject to Sharpe and Jensen's-alpha floors.
#
# Given: gross expected return g, volatility s, beta b, market return Rm, risk-free rate rf,
#        Sharpe floor S, Jensen's alpha floor A.
# Fee f (annual rate) reduces expected return one-for-one:  r_net = g - f.
# Volatility, beta, Rm and rf are unchanged by the fee.
#
# Standard conventions (no overrides in the text):
#   market risk premium        MRP = Rm - rf
#   Sharpe ratio               (r_net - rf) / s
#   Jensen's alpha             r_net - [ rf + b * (Rm - rf) ]   (CAPM required return)
#
# Constraints (both are linear in f, "at least" => non-strict inequalities):
#   Sharpe:  (g - f - rf)/s >= S            =>  f <= g - rf - S*s
#   Alpha :  g - f - rf - b*MRP >= A        =>  f <= g - rf - b*MRP - A
# Maximum feasible fee = min(f_sharpe, f_alpha), the binding (tighter) constraint.
# Both constraints hold with equality-or-slack at that exact (unrounded) rate.
# No non-negativity floor is stated in the text ("apply only the rules stated"), so the exact
# maximum is returned with its sign preserved: a negative value means even a zero fee cannot
# meet the constraints, and the constraint-satisfying maximum is a negative fee (a rebate).
# Final answer reported in percent (x100), rounded half up to 2 dp by the framework.
# Checkpoint: market risk premium Rm - rf as a plain ratio (unrounded exact).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h032"


def solve(text: str, q: dict) -> dict:
    g = grab(r"gross expected return {N}", text)
    s = grab(r"volatility {N}", text)
    b = grab(r"beta {N}", text)
    rm = grab(r"market return is {N}", text)
    rf = grab(r"risk-free rate is {N}", text)
    sharpe_min = grab(r"Sharpe ratio of at least {N}", text)
    alpha_min = grab(r"Jensen's alpha of at least {N}", text)

    mrp = rm - rf
    f_sharpe = g - rf - sharpe_min * s
    f_alpha = g - rf - b * mrp - alpha_min
    f_max = min(f_sharpe, f_alpha)

    return {"final": f_max * 100, "slots": {"market_premium_checkpoint": mrp}}
