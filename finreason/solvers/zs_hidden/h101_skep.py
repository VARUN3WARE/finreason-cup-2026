"""h101 -- fictional compliance planning policy: choose Plan A / Plan B / Neither plan.

Structure (identical across the 3 instances, numbers differ):
  inherent risk R0; for each plan P in {A, B}: per-stage fractional risk reduction f_P,
  implementation cost i_P (USD), monitoring cost m_P (USD), fractional cost credit c_P.
  residual_P = R0 * (1 - f_P) ** 3            (three sequential multiplicative stages)
  netcost_P  = (i_P + m_P) * (1 - c_P)        (credit applied to the SUM of both costs)
  qualifies_P = residual_P <= risk_threshold and netcost_P <= cost_threshold
  both qualify -> lower exact net cost (Plan A on exact tie); one -> it; none -> "Neither plan".
  checkpoint  = Plan A's one-stage retained-risk factor = 1 - f_A (unrounded; framework rounds
                half-up to 6 dp).

AMBIGUITIES HUNTED AND RESOLVED (textual evidence in brackets):
 1. Checkpoint quantity.  "one-stage retained-risk FACTOR" / slot text "retained-risk factor after one of
    the three identical sequential reduction stages" -> the per-stage multiplier (1 - f_A), NOT the risk
    level after one stage (R0 * (1 - f_A)) and NOT the three-stage residual.  Evidence: the word
    "factor"; the body names exactly this quantity ("multiply inherent risk by one minus that plan's
    per-stage fraction three successive times"); unit "ratio".  Corroboration: instance t1_sodiw... sets
    f_A = 0.2999995 so that 1 - f_A = 0.7000005 is an exact half-up tie at the 7th decimal (-> 0.700001);
    that trap only exists under this reading.  Must be exact Fraction (float 0.7000005 may round down).
 2. "Independently to six decimal places": the checkpoint is rounded for display only; we return the
    exact unrounded factor and never feed a rounded value into the residual-risk predicate ("return the
    selected plan from exact predicates and costs").
 3. Risk reduction mechanics: multiplicative on surviving risk ("apply its stated reduction to surviving
    risk ... equivalently, multiply inherent risk by one minus that plan's per-stage fraction three
    successive times") -> R0 * (1 - f) ** 3 with an exact integer power; NOT R0 - 3f, NOT R0 * (1 - 3f),
    and no replenishment between stages.
 4. Net cost base: "the sum of implementation and monitoring costs multiplied by one minus its credit
    fraction" -> (i + m) * (1 - c).  The credit is NOT applied to the monitoring cost alone, and it is a
    fraction (0.2), not a percent.  Each plan uses its OWN credit fraction ("its credit fraction").
 5. Qualification comparisons: "no more than" twice -> non-strict (<=) for both residual risk and net
    cost; "qualifies only if ... and ..." -> both must hold.  Residual risk is compared as an exact
    rational against the exact threshold (thresholds such as 0.22360029400021005 are parsed exactly).
 6. Selection rule: both qualify -> the strictly lower exact net cost wins; "with Plan A on an exact tie"
    -> A iff netcost_A <= netcost_B.  Exactly one qualifies -> that plan.  Neither -> "Neither plan".
    Residual risk plays no role in the choice beyond the qualification predicate (no risk tie-break).
 7. Units: costs and cost threshold in USD (no conversion); risk values are plain ratios; the per-stage
    reduction is a fraction of surviving risk, not a percent.
 8. Stage count: "exactly three sequential stages" -- parsed from the text (word or digit) with 3 as the
    template default; every instance says three.
 9. Enum tokens are returned verbatim: "Plan A", "Plan B", "Neither plan".
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h101"

_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _stages(text: str) -> int:
    m = re.search(r"exactly\s+(\w+)\s+sequential\s+stages", text, flags=re.I)
    if m:
        w = m.group(1).lower()
        if w in _WORDS:
            return _WORDS[w]
        if w.isdigit():
            return int(w)
    return 3


def _plan(text: str, name: str) -> dict:
    """Parse one plan's four parameters, anchored on the plan's own sentence."""
    base = (
        rf"Plan {name} has per-stage fractional risk reduction {{N}},\s*"
        rf"implementation cost {{N}} USD,\s*monitoring cost {{N}} USD,\s*"
        rf"and fractional cost credit {{N}}"
    )
    f = grab(base, text, 1)
    impl = grab(base, text, 2)
    mon = grab(base, text, 3)
    credit = grab(base, text, 4)
    return {"f": f, "impl": impl, "mon": mon, "credit": credit}


def solve(text: str, q: dict) -> dict:
    r0 = grab(r"Inherent risk is {N}", text)
    a = _plan(text, "A")
    b = _plan(text, "B")
    n = _stages(text)
    risk_thr = grab(r"residual risk is no more than {N}", text)
    cost_thr = grab(r"net cost is no more than {N} USD", text)

    def residual(p: dict) -> Fraction:
        # three successive multiplications by the retained-risk factor (exact integer power)
        return r0 * (1 - p["f"]) ** n

    def net_cost(p: dict) -> Fraction:
        return (p["impl"] + p["mon"]) * (1 - p["credit"])

    res_a, res_b = residual(a), residual(b)
    nc_a, nc_b = net_cost(a), net_cost(b)

    qual_a = res_a <= risk_thr and nc_a <= cost_thr
    qual_b = res_b <= risk_thr and nc_b <= cost_thr

    if qual_a and qual_b:
        final = "Plan A" if nc_a <= nc_b else "Plan B"   # Plan A on an exact tie
    elif qual_a:
        final = "Plan A"
    elif qual_b:
        final = "Plan B"
    else:
        final = "Neither plan"

    # Plan A's one-stage retained-risk factor, exact and unrounded (framework rounds half-up, 6 dp)
    factor_a = 1 - a["f"]

    return {"final": final, "slots": {"plan_a_residual_factor_checkpoint": factor_a}}
