# FINANCE MODEL
# V = current portfolio value, L = stressed-value floor (L < V), s = fraction of the risky
# allocation lost in the stress, c = policy cap on the risky weight (portfolio weight, ratio).
# Risky weight w -> risky dollars = w*V; the rest (1-w)*V keeps its value.
#   Stressed value = (1-w)V + w*V*(1-s) = V*(1 - w*s)
# Floor: V*(1 - w*s) >= L  <=>  w <= (V - L)/(V*s)           (stress-implied max weight)
# Loss budget (checkpoint 1): allowable dollar loss under the floor = V - L  (USD).
# Max permitted weight = min(stress-implied weight, policy cap c), kept exact/unrounded
# (the displayed 2dp percentage is only a reporting approximation). Result in percent = *100.
# No overrides of standard conventions; weight is also bounded to [0,1] (cap/implied already <=1 here).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h098"


def solve(text: str, q: dict) -> dict:
    V = grab(r"portfolio worth {N}", text)
    L = grab(r"at or above {N}", text)
    s = grab(r"risky asset loses {N} of its allocated amount", text)
    c = grab(r"caps the risky asset's portfolio weight at {N}", text)
    budget = V - L
    w_stress = budget / (V * s)
    w = min(w_stress, c, Fraction(1))
    if w < 0:
        w = Fraction(0)
    return {"final": w * 100, "slots": {"loss_budget_checkpoint": budget}}
