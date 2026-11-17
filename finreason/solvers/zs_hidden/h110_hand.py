"""h110: two social-impact programs, three independent delivery opportunities each.

Chain (per program):
  total cost       = fixed cost + aggregate per-unit delivery cost * volume   (covers all 3 opportunities)
  per-opp failure  = 1 - per-opportunity success probability
  effective prob   = 1 - failure**3        (value realized once if at least one opportunity succeeds)
  planned value    = monetized social value per unit * volume
  expected net     = planned value * effective prob - total cost
Feasible  <=> total cost <= budget ("does not exceed") and volume >= minimum ("reaches").
Decision: both feasible -> higher expected net (tie -> program_a); one feasible -> that one;
none -> no_feasible_program.
Checkpoint: per-opportunity failure probability of program A (1 - p_A), unrounded.
"""

from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h110"


def _program(fixed, unit_cost, volume, value_per_unit, p_success):
    total_cost = fixed + unit_cost * volume
    fail = 1 - p_success
    effective = 1 - fail ** 3
    planned_value = value_per_unit * volume
    expected_net = planned_value * effective - total_cost
    return total_cost, fail, effective, expected_net


def solve(text: str, q: dict) -> dict:
    # Program A inputs (named explicitly in the text).
    fa = grab(r"program A,? with fixed cost {N}", text)
    ca = grab(r"aggregate delivery cost per beneficiary-equivalent unit {N}", text)
    va = grab(r"beneficiary-equivalent volume {N}", text)
    sa = grab(r"monetized social value per unit {N}", text)
    pa = grab(r"per-opportunity success probability {N}", text)

    # Program B inputs, in the same order: fixed cost, unit cost, volume, value per unit, probability.
    fb, cb, vb, sb, pb = grab_all(
        r"program B with corresponding inputs {N},\s*{N},\s*{N},\s*{N},?\s*(?:and\s+)?{N}", text
    )

    budget = grab(r"total cost does not exceed {N}", text)
    min_volume = grab(r"volume reaches {N}", text)

    tca, fail_a, _, eva = _program(fa, ca, va, sa, pa)
    tcb, _, _, evb = _program(fb, cb, vb, sb, pb)

    feas_a = tca <= budget and va >= min_volume
    feas_b = tcb <= budget and vb >= min_volume

    if feas_a and feas_b:
        final = "program_a" if eva >= evb else "program_b"
    elif feas_a:
        final = "program_a"
    elif feas_b:
        final = "program_b"
    else:
        final = "no_feasible_program"

    return {
        "final": final,
        "slots": {
            "program_a_failure_probability_checkpoint": Fraction(fail_a),
        },
    }
