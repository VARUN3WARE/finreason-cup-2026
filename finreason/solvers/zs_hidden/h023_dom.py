# FINANCE MODEL (h023): leverage-covenant ratchet, choose between two capital plans.
#
# Quantities:
#   c0 = starting permitted debt-to-equity ceiling (stated, 1.00).
#   t  = fraction by which the remaining ceiling is reduced at EACH stage (multiplicative ratchet,
#        not additive): ceiling after k stages = c0 * (1 - t)^k.
#   Checkpoint "one_stage_leverage_cap_checkpoint" = ceiling remaining after ONE stage = c0 * (1 - t)
#        (plain ratio, unrounded Fraction; the framework rounds to 6 dp half-up).
#   Final shared ceiling = c0 * (1 - t)^3  (three stages; stated as (1-t)^3 with c0 = 1).
#   Post-transaction debt-to-equity ratio (exact rational):
#        Plan A: (D + new borrowing) / (E + new equity)
#        Plan B: (D - debt repaid)   / (E + new equity)
#   A plan qualifies iff ratio <= final ceiling (non-strict: "does not exceed").
#   Decision: among qualifying plans pick the lower exact ratio; exact tie -> plan_a;
#             no qualifier -> neither_plan. Only one qualifier -> that plan.
# No overrides of standard conventions beyond the text (scenario-specific policy, no real-world law).
# All arithmetic exact with Fraction (integer powers only); nothing rounded inside the computation.

from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h023"

_STAGE_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}


def solve(text: str, q: dict) -> dict:
    d0, e0 = grab_all(r"current debt {N} and current equity {N}", text)
    c0 = grab(r"ceiling starts at {N}", text)
    t = grab(r"fraction t\s*=\s*{N}", text)
    ba, ea = grab_all(r"Plan A adds borrowing {N} and equity {N}", text)
    rb, eb = grab_all(r"Plan B repays debt {N} and adds equity {N}", text)

    import re
    m = re.search(r"(\w+)-stage", text)
    stages = _STAGE_WORDS.get(m.group(1).lower(), 3) if m else 3

    one_stage = c0 * (1 - t)
    final_cap = c0 * (1 - t) ** stages

    ratio_a = (d0 + ba) / (e0 + ea)
    ratio_b = (d0 - rb) / (e0 + eb)

    qa = ratio_a <= final_cap
    qb = ratio_b <= final_cap

    if qa and qb:
        final = "plan_a" if ratio_a <= ratio_b else "plan_b"
    elif qa:
        final = "plan_a"
    elif qb:
        final = "plan_b"
    else:
        final = "neither_plan"

    return {"final": final, "slots": {"one_stage_leverage_cap_checkpoint": one_stage}}
