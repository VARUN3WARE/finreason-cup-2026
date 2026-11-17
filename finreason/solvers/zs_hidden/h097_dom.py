# MODEL (h097): two-gap regulatory remediation under a budget.
#   cap_gap  = max(0, required_capital - current_capital)       (floored at 0 even though text says "requirements exceed
#                                                                 resources"; a surplus never costs money / never gives credit)
#   liq_gap  = max(0, required_liquidity - liquid_assets)
#   cost_c, cost_l = per-dollar cost of closing capital / liquidity gap
#   filing   = fixed cost of ANY submitted plan; budget = total budget
#   full plan cost   = cost_c*cap_gap + cost_l*liq_gap + filing ; affordable iff <= budget
#   If full plan affordable -> full_remediation.
#   Otherwise pick the single-gap plan for the LARGER gap in dollar terms (not cost terms):
#       cap_gap >= liq_gap -> capital_priority (exact tie -> capital_priority); liq_gap > cap_gap -> liquidity_priority
#       plan cost = cost_x*gap_x + filing ; return token iff <= budget, else no_feasible_plan.
#   Checkpoint capital_coverage = current_capital / required_capital  (plain ratio, share of requirement already held;
#       NOT capped at 1 because the text states no cap; round half-up at 6dp by the framework).
# Overrides: none to standard conventions; "affordable" = cost <= budget (spending exactly the budget is allowed).
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h097"


def solve(text: str, q: dict) -> dict:
    cur_c, req_c = grab_all(r"current capital {N} against required capital {N}", text)
    cur_l, req_l = grab_all(r"liquid assets {N} against required liquidity {N}", text)
    cost_c = grab(r"[Cc]losing one dollar of capital gap costs ratio {N}", text)
    cost_l = grab(r"[Cc]losing one dollar of liquidity gap costs ratio {N}", text)
    filing = grab(r"every submitted plan also costs {N}", text)
    budget = grab(r"total budget is {N}", text)

    gap_c = max(Fraction(0), req_c - cur_c)
    gap_l = max(Fraction(0), req_l - cur_l)

    full_cost = cost_c * gap_c + cost_l * gap_l + filing
    if full_cost <= budget:
        final = "full_remediation"
    else:
        if gap_c >= gap_l:
            token, plan_cost = "capital_priority", cost_c * gap_c + filing
        else:
            token, plan_cost = "liquidity_priority", cost_l * gap_l + filing
        final = token if plan_cost <= budget else "no_feasible_plan"

    return {"final": final, "slots": {"capital_coverage_checkpoint": cur_c / req_c}}
