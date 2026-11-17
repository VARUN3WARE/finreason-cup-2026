"""h072 -- literal transcription: two residual-value revision scenarios, three-subperiod
declining depreciation on the balance above residual, qualify-then-pick-lower rule."""

import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h072"

SUBPERIODS_WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6}


def solve(text: str, q: dict) -> dict:
    # "An asset has original cost C and accumulated depreciation of AD in USD millions."
    original_cost = grab(r"original cost {N}", text)
    accumulated_dep = grab(r"accumulated depreciation of {N}", text)
    carrying_amount = original_cost - accumulated_dep

    # "Scenario A revises residual value to RA and applies per-subperiod depreciation ratio rA;"
    res_a = grab(r"Scenario A revises residual value to {N}", text)
    ratio_a = grab(r"Scenario A revises residual value to [^;]*?depreciation ratio {N}", text)
    # "Scenario B uses RB and rB."
    res_b = grab(r"Scenario B uses {N}", text)
    ratio_b = grab(r"Scenario B uses {N} and {N}", text, group=2)

    # "the next reporting interval contains exactly three equal sequential subperiods"
    n = 3
    m = re.search(r"contains exactly (\w+) equal sequential subperiods", text)
    if m and m.group(1).lower() in SUBPERIODS_WORDS:
        n = SUBPERIODS_WORDS[m.group(1).lower()]
    elif m and m.group(1).isdigit():
        n = int(m.group(1))

    # "A scenario qualifies only if its exact cumulative three-stage depreciation is at most X
    #  and its remaining depreciable balance above residual is at least Y."
    cap_cum = grab(r"cumulative [\w-]+ depreciation is at most {N}", text)
    floor_rem = grab(r"remaining depreciable balance above residual is at least {N}", text)

    def run(residual: Fraction, ratio: Fraction):
        # balance above residual value; residual itself is not depreciated
        balance = carrying_amount - residual
        if balance < 0:
            balance = Fraction(0)
        cumulative = Fraction(0)
        for _ in range(n):
            dep = ratio * balance  # ratio applies again to the balance above residual
            cumulative += dep
            balance -= dep
        return cumulative, balance

    cum_a, rem_a = run(res_a, ratio_a)
    cum_b, rem_b = run(res_b, ratio_b)

    qual_a = cum_a <= cap_cum and rem_a >= floor_rem
    qual_b = cum_b <= cap_cum and rem_b >= floor_rem

    # "Return the qualifying scenario with lower exact cumulative depreciation,
    #  choose Scenario A on an exact tie, or return Neither scenario when neither qualifies."
    if qual_a and qual_b:
        final = "Scenario A" if cum_a <= cum_b else "Scenario B"
    elif qual_a:
        final = "Scenario A"
    elif qual_b:
        final = "Scenario B"
    else:
        final = "Neither scenario"

    # Checkpoint: Scenario A's one-subperiod balance-retention factor = 1 - ratio_A
    retention_a = 1 - ratio_a

    return {
        "final": final,
        "slots": {"a_one_stage_retention_factor_checkpoint": retention_a},
    }
