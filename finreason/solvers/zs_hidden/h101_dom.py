# ======================================================================================
# FINANCE MODEL (h101) -- fictional compliance-planning policy: choose between Plan A
# and Plan B (mutually exclusive) on residual risk and net cost.
# ======================================================================================
#
# Economic objects (per plan p in {A, B}), all exact rationals:
#   R0   inherent risk (a plain ratio / score, same for both plans; here 0.8).
#   r_p  per-stage FRACTIONAL risk reduction: the fraction of the *surviving* risk that a
#        single stage removes.
#   k_p  = 1 - r_p  : the one-stage RETAINED-RISK FACTOR (fraction of surviving risk that
#        remains after one stage).  This is the multiplicative factor the text describes
#        ("one minus that plan's per-stage fraction").
#   n    number of identical sequential stages (text: "exactly three"; parsed, = 3).
#   I_p  implementation cost (USD),  M_p monitoring cost (USD),  c_p fractional cost credit.
#
# Risk side:
#   Each stage acts on the risk that survived the previous stage, with no replenishment,
#   so stages compound geometrically:
#       residual_p = R0 * k_p ** n = R0 * (1 - r_p) ** 3          (integer power, exact)
#   NOT additive (R0*(1-3r)) and NOT 1 - r**3; the text states the multiplicative form
#   explicitly ("multiply inherent risk by one minus that plan's per-stage fraction three
#   successive times").
#
# Cost side:
#   gross cost  = I_p + M_p                       (sum of implementation and monitoring)
#   net cost    = (I_p + M_p) * (1 - c_p)         (the credit fraction is a haircut on the
#                                                  whole summed cost; "the sum ... multiplied
#                                                  by one minus its credit fraction")
#   USD, a one-shot total: the text gives no timing, no discount rate, no time value, so no
#   discounting is applied.  (Alternative parse I + M*(1-c) was checked: it does not change
#   any of the three selections, but the cost caps in the instances sit between the two
#   plans' (I+M)(1-c) values, which confirms the intended reading.)
#
# Qualification (both tests INCLUSIVE, "no more than" means <=):
#       qualifies_p  <=>  residual_p <= residual_cap   AND   net_cost_p <= cost_cap (USD)
#   Caps are parsed as the exact decimals printed (e.g. 0.22360029400021005 is used exactly,
#   not as a float).  Because the comparison is on exact rationals there is no float
#   boundary error.
#
# Selection rule (exactly as worded):
#   both qualify  -> the plan with the LOWER exact net cost; exact tie -> "Plan A"
#                    (risk is NOT a tie-breaker and is NOT part of the cost comparison;
#                     the lower-risk plan can lose if it costs more)
#   exactly one   -> that plan
#   neither       -> "Neither plan"
#
# Checkpoint (single slot, position 1):
#   plan_a_residual_factor_checkpoint = k_A = 1 - r_A   (ratio, unit "ratio", NOT percent,
#   and NOT multiplied by the inherent risk: it is the *factor*, not the residual risk after
#   one stage).  Returned UNROUNDED; the framework rounds to 6 decimals half-up.  "Independently"
#   means the decision uses exact values, never the displayed/rounded checkpoint.
#   (Instance 2 has r_A = 0.2999995 -> k_A = 0.7000005, an exact half-up tie at the 6th
#   decimal, which renders 0.700001: consistent with this being the intended checkpoint.)
#
# Conventions overridden / notes:
#   * No real-world law or guidance is applied (fictional scenario-local policy).
#   * No rounding inside the computation: the problem states no whole-unit/cent rounding
#     that feeds downstream, so every intermediate stays an exact Fraction.
#   * Only stated rules are used: no discounting, no probability weighting, no replenishment.
# ======================================================================================

import re
from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h101"

_WORD_TO_INT = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

SLOT_ID = "plan_a_residual_factor_checkpoint"


def _stage_count(text: str) -> int:
    """Number of sequential stages, e.g. 'in exactly three sequential stages'."""
    m = re.search(r"exactly\s+(\w+)\s+sequential\s+stages", text)
    if m is None:
        raise ValueError("stage count not found")
    tok = m.group(1).lower()
    if tok.isdigit():
        return int(tok)
    return _WORD_TO_INT[tok]


def _plan_inputs(segment: str):
    """(per-stage reduction r, implementation I, monitoring M, credit c) from one plan sentence."""
    r = grab(r"per-stage fractional risk reduction {N}", segment)
    impl = grab(r"implementation cost {N} USD", segment)
    mon = grab(r"monitoring cost {N} USD", segment)
    credit = grab(r"fractional cost credit {N}", segment)
    return r, impl, mon, credit


def solve(text: str, q: dict) -> dict:
    inherent = grab(r"Inherent risk is {N}", text)

    ia = text.index("Plan A has")
    ib = text.index("Plan B has")
    ie = text.index("For each plan")
    seg_a = text[ia:ib]
    seg_b = text[ib:ie]

    n = _stage_count(text)

    cap_res, cap_cost = grab_all(
        r"residual risk is no more than {N} and net cost is no more than {N} USD", text
    )

    def evaluate(segment: str):
        r, impl, mon, credit = _plan_inputs(segment)
        retained = 1 - r                          # one-stage retained-risk factor
        residual = inherent * retained ** n       # exact integer power, compounding stages
        net = (impl + mon) * (1 - credit)         # credit haircut on the summed cost
        ok = (residual <= cap_res) and (net <= cap_cost)
        return retained, residual, net, ok

    ret_a, res_a, net_a, ok_a = evaluate(seg_a)
    _ret_b, res_b, net_b, ok_b = evaluate(seg_b)

    if ok_a and ok_b:
        final = "Plan A" if net_a <= net_b else "Plan B"   # lower exact net cost; tie -> Plan A
    elif ok_a:
        final = "Plan A"
    elif ok_b:
        final = "Plan B"
    else:
        final = "Neither plan"

    return {"final": final, "slots": {SLOT_ID: Fraction(ret_a)}}
