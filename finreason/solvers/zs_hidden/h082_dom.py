# FINANCE MODEL (h082): abate-then-buy vs credits-only carbon compliance.
#
# Inputs: obligation O (tCO2e), abatement capacity C, availability flag A (true/false),
#   fixed abatement cost FC (USD), variable abatement cost v (USD/t), credit price p (USD/t),
#   credit supply cap S (ton-equivalent credits; 1 credit = 1 ton).
#
# Abate-then-buy (fixed, non-optimised):
#   abated quantity q = min(O, C) if A is true, else 0 (abatement unavailable -> nothing abated).
#   residual r = O - q, bought as credits (r credits).
#   variable abatement cost  V = v * q          <- the checkpoint (USD, half-up 2dp)
#   total cost = FC + V + p * r
#   feasible iff A is true and r <= S.
# Credits-only:
#   buy O credits; cost = p * O; feasible iff O <= S.
# Decision: lower-cost feasible strategy; tie -> abate_then_buy; sole feasible -> that one;
#   neither feasible -> no_feasible_strategy.
# Overrides / interpretations: when A is false the abate-then-buy strategy is infeasible and
#   the abated quantity (hence variable abatement cost checkpoint) is 0.
from fractions import Fraction
from finreason.nums import grab, F

TEMPLATE_ID = "h082"


def solve(text: str, q: dict) -> dict:
    import re
    O = grab(r"compliance obligation of {N} tons", text)
    C = grab(r"internal abatement capacity {N} tons", text)
    m = re.search(r"operational availability (true|false)", text)
    avail = m.group(1) == "true"
    FC = grab(r"fixed cost {N} USD", text)
    v = grab(r"variable cost {N} USD per ton", text)
    p = grab(r"Carbon credits cost {N} USD per ton", text)
    S = grab(r"at most {N} ton-equivalent credits", text)

    qty = min(O, C) if avail else Fraction(0)
    resid = O - qty
    var_total = v * qty
    abate_feasible = avail and resid <= S
    abate_cost = FC + var_total + p * resid
    credit_feasible = O <= S
    credit_cost = p * O

    if abate_feasible and credit_feasible:
        final = "abate_then_buy" if abate_cost <= credit_cost else "credits_only"
    elif abate_feasible:
        final = "abate_then_buy"
    elif credit_feasible:
        final = "credits_only"
    else:
        final = "no_feasible_strategy"

    return {"final": final, "slots": {"variable_abatement_total_checkpoint": var_total}}
