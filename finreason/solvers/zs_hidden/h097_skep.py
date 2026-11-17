"""h097 -- scenario-local compliance policy: full / single-gap remediation plan.

AMBIGUITY RESOLUTIONS (skeptic pass)
------------------------------------
1. Gap definition. capital_gap = required_capital - current_capital, floored at
   zero (likewise for liquidity). One instance has current capital ABOVE the
   requirement; a negative gap cannot be "closed", so it contributes zero cost.
   (For the 3 instances the final token is the same with or without the floor.)
2. Cost model. "Closing one dollar of capital gap costs ratio r" -> cost of
   closing the whole gap = gap * r (a per-dollar cost, not a percent).
3. Filing cost. "every submitted plan also costs F" -> ONE filing cost is added
   to whichever plan is submitted (full plan or single-gap plan). The full plan
   is "both gaps plus filing" = cap_cost + liq_cost + F (one filing, not two).
4. Affordable. cost <= budget (non-strict). No instance sits exactly on the
   budget, so strict vs non-strict is not outcome-bearing here.
5. Larger gap. Compared in dollar-gap units (the text says "exact gap tie"),
   NOT in cost units. Tie -> capital_priority; liquidity strictly larger ->
   liquidity_priority; capital strictly larger -> capital_priority.
6. No fallback. If the prescribed single-gap plan is unaffordable, return
   no_feasible_plan even when the OTHER single-gap plan would be affordable
   ("return the prescribed token only if that plan is affordable, and return
   no_feasible_plan otherwise").
7. Checkpoint "share of required capital already covered" = current_capital /
   required_capital, exact and UNCAPPED (a coverage ratio above 1 is reported
   as such, e.g. 1.016201). Unit: ratio.
8. "Requirements exceed current resources" is a scene-setting assertion, not an
   input; it is not used (and it is false for capital in one instance).
"""

from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h097"


def solve(text: str, q: dict) -> dict:
    cur_cap, req_cap = grab_all(
        r"current capital {N} against required capital {N}", text
    )
    cur_liq, req_liq = grab_all(
        r"liquid assets {N} against required liquidity {N}", text
    )
    c_cap = grab(r"capital gap costs ratio {N}", text)
    c_liq = grab(r"liquidity gap costs ratio {N}", text)
    filing = grab(r"plan also costs {N}", text)
    budget = grab(r"total budget is {N}", text)

    zero = Fraction(0)
    cap_gap = max(zero, req_cap - cur_cap)
    liq_gap = max(zero, req_liq - cur_liq)

    cap_cost = cap_gap * c_cap
    liq_cost = liq_gap * c_liq

    full_cost = cap_cost + liq_cost + filing
    if full_cost <= budget:
        final = "full_remediation"
    else:
        if cap_gap >= liq_gap:  # exact tie -> capital_priority
            token, plan_cost = "capital_priority", cap_cost + filing
        else:
            token, plan_cost = "liquidity_priority", liq_cost + filing
        final = token if plan_cost <= budget else "no_feasible_plan"

    coverage = cur_cap / req_cap

    return {
        "final": final,
        "slots": {"capital_coverage_checkpoint": coverage},
    }
