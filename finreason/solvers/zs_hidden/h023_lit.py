"""h023 -- three-stage leverage-covenant ratchet; compare two capital plans (literal transcription)."""

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h023"


def solve(text: str, q: dict) -> dict:
    # "Compare two capital plans for a company with current debt D and current equity E."
    debt0 = grab(r"current debt {N}", text)
    equity0 = grab(r"current equity {N}", text)

    # "the permitted debt-to-equity ceiling starts at 1.00."
    ceiling_start = grab(r"ceiling starts at {N}", text)

    # "At each stage the company reduces the remaining ceiling by the same fraction t=..."
    t = grab(r"same fraction t\s*=\s*{N}", text)

    # Three-stage ratchet: each stage multiplies the remaining ceiling by (1 - t).
    stages = 3
    ceilings = [ceiling_start]
    for _ in range(stages):
        ceilings.append(ceilings[-1] * (1 - t))
    one_stage_ceiling = ceilings[1]
    # "so the final shared ceiling is (1-t)^3" (starting ceiling 1.00)
    final_ceiling = ceilings[stages]
    assert final_ceiling == ceiling_start * (1 - t) ** 3

    # "Plan A adds borrowing X and equity Y."
    a_borrow = grab(r"Plan A adds borrowing {N}", text)
    a_equity = grab(r"Plan A adds borrowing [^.]*?and equity {N}", text)
    a_debt = debt0 + a_borrow
    a_eq = equity0 + a_equity
    ratio_a = Fraction(a_debt) / Fraction(a_eq)

    # "Plan B repays debt X and adds equity Y."
    b_repay = grab(r"Plan B repays debt {N}", text)
    b_equity = grab(r"Plan B repays debt [^.]*?adds equity {N}", text)
    b_debt = debt0 - b_repay
    b_eq = equity0 + b_equity
    ratio_b = Fraction(b_debt) / Fraction(b_eq)

    # "A plan qualifies only when its exact post-transaction ratio does not exceed the final ceiling."
    a_ok = ratio_a <= final_ceiling
    b_ok = ratio_b <= final_ceiling

    # Select qualifying plan with lower exact ratio; plan_a on exact tie; neither_plan if none qualifies.
    if a_ok and b_ok:
        final = "plan_a" if ratio_a <= ratio_b else "plan_b"
    elif a_ok:
        final = "plan_a"
    elif b_ok:
        final = "plan_b"
    else:
        final = "neither_plan"

    return {
        "final": final,
        "slots": {"one_stage_leverage_cap_checkpoint": one_stage_ceiling},
    }
