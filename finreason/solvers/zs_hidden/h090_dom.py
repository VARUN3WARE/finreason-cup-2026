# MODEL (h090): leverage-covenant screen between two financing packages.
#
# Balance sheet identity: Assets = Liabilities + Equity.
#   Start: assets A0, liabilities L0, equity E0 = A0 - L0.
#   A package adds equity proceeds e and debt proceeds d. Both are cash received,
#   so assets rise by e + d; liabilities rise by d only (debt is a liability);
#   equity rises by e only.
#       assets_post      = A0 + e + d
#       liabilities_post = L0 + d
#       equity_post      = assets_post - liabilities_post = E0 + e
#       ratio            = liabilities_post / assets_post   (exact Fraction)
#
# Ratchet: three stages, each reducing the remaining ceiling by fraction t, from a
# start of 1.00, so after one stage the cap factor is (1 - t) and the final
# cumulative ceiling is (1 - t)^3 (integer power, exact Fraction arithmetic).
# Checkpoint "one-stage liabilities-to-assets cap factor" = 1 - t (ratio, unrounded).
#
# Qualification (a scenario rule, not real-world law): equity_post >= minimum equity
# (inclusive) AND ratio <= final ceiling (inclusive, exact comparison).
# Decision: among qualifying packages return the one with the lower exact ratio;
# tie -> Package A; neither qualifies -> "Neither package".
#
# Overrides of standard conventions: none.

from fractions import Fraction

from finreason.nums import grab, F  # noqa: F401

TEMPLATE_ID = "h090"


def solve(text: str, q: dict) -> dict:
    a0 = grab(r"assets of {N} and liabilities of", text)
    l0 = grab(r"liabilities of {N} in USD millions", text)

    ea = grab(r"Package A adds equity proceeds of {N} and debt proceeds", text)
    da = grab(r"Package A adds equity proceeds of [-\d.,/]+ and debt proceeds of {N}", text)
    eb = grab(r"Package B adds equity proceeds of {N} and debt proceeds", text)
    db = grab(r"Package B adds equity proceeds of [-\d.,/]+ and debt proceeds of {N}", text)

    t = grab(r"same fraction {N}", text)
    min_equity = grab(r"post-financing equity is at least {N}", text)

    one_stage = 1 - t
    ceiling = one_stage ** 3

    def evaluate(e, d):
        assets = a0 + e + d
        liabilities = l0 + d
        equity = assets - liabilities
        ratio = liabilities / assets
        ok = (equity >= min_equity) and (ratio <= ceiling)
        return ok, ratio

    ok_a, r_a = evaluate(ea, da)
    ok_b, r_b = evaluate(eb, db)

    if ok_a and ok_b:
        final = "Package A" if r_a <= r_b else "Package B"
    elif ok_a:
        final = "Package A"
    elif ok_b:
        final = "Package B"
    else:
        final = "Neither package"

    return {
        "final": final,
        "slots": {"one_stage_leverage_cap_checkpoint": one_stage},
    }
