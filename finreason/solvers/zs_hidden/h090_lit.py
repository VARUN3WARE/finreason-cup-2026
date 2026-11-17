"""h090 -- two financing packages vs. a three-stage ratcheted leverage ceiling (literal transcription)."""
from fractions import Fraction
from finreason.nums import grab, grab_all, F

TEMPLATE_ID = "h090"


def solve(text: str, q: dict) -> dict:
    # "A company begins with assets of X and liabilities of Y in USD millions."
    assets0, liab0 = grab_all(r"begins with assets of {N} and liabilities of {N}", text)
    equity0 = assets0 - liab0

    # "Financing Package A adds equity proceeds of E and debt proceeds of D."
    eqA, debtA = grab_all(r"Package A adds equity proceeds of {N} and debt proceeds of {N}", text)
    eqB, debtB = grab_all(r"Package B adds equity proceeds of {N} and debt proceeds of {N}", text)

    # "the permitted liabilities-to-assets ceiling starts at C0."
    c0 = grab(r"ceiling starts at {N}", text)
    # "At each stage, the company reduces the remaining ceiling by the same fraction t"
    t = grab(r"remaining ceiling by the same fraction {N}", text)
    # three stages: "the final cumulative ceiling is (1-t)^3" (times the starting ceiling of 1.00)
    stages = 3
    ceiling = c0
    for _ in range(stages):
        ceiling = ceiling * (1 - t)
    # Checkpoint: "one-stage liabilities-to-assets cap factor" = the factor applied in ONE stage,
    # i.e. the ceiling remaining after one stage starting from 1.00: (1 - t).  (Not the cumulative (1-t)^3.)
    cap_factor = 1 - t

    # "post-financing equity is at least E_min"
    eq_min = grab(r"post-financing equity is at least {N}", text)

    def evaluate(eq_add, debt_add):
        assets = assets0 + eq_add + debt_add
        liabs = liab0 + debt_add
        equity = assets - liabs  # = equity0 + eq_add
        ratio = liabs / assets
        qualifies = (equity >= eq_min) and (ratio <= ceiling)
        return qualifies, ratio

    qa, ra = evaluate(eqA, debtA)
    qb, rb = evaluate(eqB, debtB)

    if qa and qb:
        final = "Package A" if ra <= rb else "Package B"
    elif qa:
        final = "Package A"
    elif qb:
        final = "Package B"
    else:
        final = "Neither package"

    return {"final": final, "slots": {"one_stage_leverage_cap_checkpoint": cap_factor}}
