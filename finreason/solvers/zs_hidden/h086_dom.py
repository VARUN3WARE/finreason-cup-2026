# FINANCE MODEL (h086): one-period expansion / defensive / wait decision.
#
# Inputs
#   R  = starting revenue
#   d  = downturn ratio      -> revenue falls by the fraction d:  R_down = R * (1 - d)
#   g  = recovery ratio      -> revenue then rebounds by g:       R_exp  = R_down * (1 + g)
#                               (only if the cash outlay K is made)
#   K  = one-period cash outlay (needed for the expansion)
#   C  = baseline operating cost; inflated cost  C_inf = C * (1 + i)  (i = cost-inflation ratio)
#   Cash = available cash;  S = required one-period scenario surplus ("at least" -> >=)
#
# Scenario surpluses
#   Expansion surplus = R * (1 - d) * (1 + g) - C_inf - K
#   Defensive surplus = R * (1 - d) - C_inf
#
# Decision
#   expansion : expansion surplus >= S  AND  Cash >= K   (cash must cover the outlay; tie passes)
#   defensive : else, defensive surplus >= S
#   wait      : else
#
# Checkpoint
#   post_downturn_checkpoint = revenue after the downturn = R * (1 - d)   (USD, unrounded here)
#
# Interpretation notes (evidence from the instances):
#   * "downturn ratio 0.5/0.01" is a decline fraction (revenue*(1-d)); instance 3's odd revenue
#     99133/990 is chosen so that R*(1-0.01) = 99.133 exactly; instance 2 gives defensive surplus
#     102 - 61 = 41 = threshold exactly (a deliberate tie, resolved by "at least").
#   * recovery ratio 0 means no rebound, so recovery multiplies by (1 + g).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h086"


def solve(text: str, q: dict) -> dict:
    R = grab(r"starts with revenue {N}", text)
    d = grab(r"downturn ratio {N}", text)
    g = grab(r"recovery ratio {N}", text)
    K = grab(r"cash outlay {N}", text)
    C = grab(r"[Bb]aseline operating cost {N}", text)
    infl = grab(r"cost-inflation ratio {N}", text)
    cash = grab(r"available cash {N}", text)
    S = grab(r"surplus of at least {N}", text)

    c_inf = C * (1 + infl)
    rev_down = R * (1 - d)
    rev_exp = rev_down * (1 + g)

    exp_surplus = rev_exp - c_inf - K
    def_surplus = rev_down - c_inf

    if exp_surplus >= S and cash >= K:
        final = "expansion"
    elif def_surplus >= S:
        final = "defensive"
    else:
        final = "wait"

    return {"final": final, "slots": {"post_downturn_checkpoint": rev_down}}
