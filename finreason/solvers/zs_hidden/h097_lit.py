"""h097 -- compliance remediation plan choice (literal transcription)."""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h097"


def solve(text: str, q: dict) -> dict:
    # "an institution has current capital X against required capital Y"
    current_capital = grab(r"current capital {N} against required capital", text)
    required_capital = grab(r"against required capital {N}", text)
    # "and liquid assets X against required liquidity Y"
    liquid_assets = grab(r"liquid assets {N} against required liquidity", text)
    required_liquidity = grab(r"against required liquidity {N}", text)
    # "Closing one dollar of capital gap costs ratio a, ... liquidity gap costs ratio b"
    capital_unit_cost = grab(r"capital gap costs ratio {N}", text)
    liquidity_unit_cost = grab(r"liquidity gap costs ratio {N}", text)
    # "every submitted plan also costs F, and the total budget is B"
    filing_cost = grab(r"every submitted plan also costs {N}", text)
    budget = grab(r"total budget is {N}", text)

    # Checkpoint: share of required capital already covered.
    capital_coverage = current_capital / required_capital

    # "Requirements exceed current resources": gaps are shortfalls, floored at zero.
    capital_gap = max(Fraction(0), required_capital - current_capital)
    liquidity_gap = max(Fraction(0), required_liquidity - liquid_assets)

    capital_cost = capital_gap * capital_unit_cost
    liquidity_cost = liquidity_gap * liquidity_unit_cost

    # "Use full_remediation when both gaps plus filing are affordable."
    full_cost = capital_cost + liquidity_cost + filing_cost
    if full_cost <= budget:
        final = "full_remediation"
    else:
        # "prescribe the single-gap plan for the larger gap, using capital_priority on an
        # exact gap tie and liquidity_priority when the liquidity gap is larger"
        if liquidity_gap > capital_gap:
            prescribed = "liquidity_priority"
            plan_cost = liquidity_cost + filing_cost
        else:
            prescribed = "capital_priority"
            plan_cost = capital_cost + filing_cost
        # "return the prescribed token only if that plan is affordable"
        final = prescribed if plan_cost <= budget else "no_feasible_plan"

    return {"final": final, "slots": {"capital_coverage_checkpoint": capital_coverage}}
