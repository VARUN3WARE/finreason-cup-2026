from fractions import Fraction
from finreason.nums import grab, grab_all, F

TEMPLATE_ID = "h072"


def solve(text: str, q: dict) -> dict:
    cost = grab(r"original cost {N}", text)
    acc = grab(r"accumulated depreciation of {N}", text)
    res_a, r_a = grab_all(r"Scenario A revises residual value to {N} and applies per-subperiod depreciation ratio {N}", text)
    res_b, r_b = grab_all(r"Scenario B uses {N} and {N}", text)
    cap = grab(r"cumulative three-stage depreciation is at most {N}", text)
    floor_rem = grab(r"remaining depreciable balance above residual is at least {N}", text)

    book = cost - acc

    def run(res, r):
        base = book - res          # balance above residual value
        bal = base
        cum = Fraction(0)
        for _ in range(3):
            d = r * bal
            cum += d
            bal -= d
        qualifies = (cum <= cap) and (bal >= floor_rem)
        return cum, bal, qualifies

    cum_a, rem_a, ok_a = run(res_a, r_a)
    cum_b, rem_b, ok_b = run(res_b, r_b)

    if ok_a and ok_b:
        final = "Scenario A" if cum_a <= cum_b else "Scenario B"
    elif ok_a:
        final = "Scenario A"
    elif ok_b:
        final = "Scenario B"
    else:
        final = "Neither scenario"

    return {"final": final, "slots": {"a_one_stage_retention_factor_checkpoint": 1 - r_a}}
