"""h097: capital/liquidity remediation plan choice under a budget (enum) + capital coverage checkpoint."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h097"


def solve(text: str, q: dict) -> dict:
    cur_cap = grab(r"current capital {N}", text)
    req_cap = grab(r"required capital {N}", text)
    cur_liq = grab(r"liquid assets {N}", text)
    req_liq = grab(r"required liquidity {N}", text)
    cap_cost = grab(r"one dollar of capital gap costs(?: ratio)? {N}", text)
    liq_cost = grab(r"one dollar of liquidity gap costs(?: ratio)? {N}", text)
    filing = grab(r"every submitted plan also costs {N}", text)
    budget = grab(r"total budget is {N}", text)

    # Checkpoint: share of required capital already covered = current / required.
    coverage = Fraction(cur_cap) / Fraction(req_cap)

    # Gaps cannot be negative: a resource already above its requirement has nothing to close.
    cap_gap = max(req_cap - cur_cap, Fraction(0))
    liq_gap = max(req_liq - cur_liq, Fraction(0))

    full_cost = cap_gap * cap_cost + liq_gap * liq_cost + filing
    if full_cost <= budget:
        final = "full_remediation"
    else:
        # Single-gap plan for the larger gap; exact tie -> capital_priority.
        if liq_gap > cap_gap:
            token, plan_cost = "liquidity_priority", liq_gap * liq_cost + filing
        else:
            token, plan_cost = "capital_priority", cap_gap * cap_cost + filing
        final = token if plan_cost <= budget else "no_feasible_plan"

    return {"final": final, "slots": {"capital_coverage_checkpoint": coverage}}
