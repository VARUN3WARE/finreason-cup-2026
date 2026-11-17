"""Cluster h110 -- social-impact program A vs program B with three independent delivery opportunities.

AMBIGUITY HUNT (each point where two analysts could disagree, with the textual resolution):

1. "planned monetized social value" is never given as one number.  Resolution: it is
   (monetized social value per unit) x (beneficiary-equivalent volume).  The inputs are "per
   unit" and "volume", and the text says planned value "is realized once, not once per success",
   i.e. the per-unit value times the whole volume, realized a single time.
2. Total cost: "fixed cost plus aggregate per-unit delivery cost multiplied by volume" ->
   TC = fixed + unit_cost * volume (multiplication binds first; the sentence says exactly that).
   The stated total cost "covers all three opportunities" -> it is NOT multiplied by three.
3. Effective delivery probability: "one minus the probability that all three opportunities fail"
   with independent opportunities sharing one probability p -> P_eff = 1 - (1-p)^3 (exact Fraction
   power with an integer exponent).  The social value is realized once (not once per success), so
   expected gross value = planned value * P_eff, NOT planned value * 3p.
4. Expected net social value = planned value * P_eff - TC (the text gives this formula verbatim).
   No positivity requirement is stated anywhere: a feasible program with negative expected net
   value is still chosen if it is the sole feasible one or the higher of two.
5. Feasibility: "total cost does not exceed X" -> TC <= X (equality feasible);
   "its volume reaches Y" -> volume >= Y (equality feasible: instance 3 has volume 81 vs minimum 81).
   Both conditions must hold ("only when ... and ...").  The same X and Y apply to both programs.
6. Decision rule, in the stated order: both feasible -> higher expected net value, exact tie ->
   program_a; exactly one feasible -> that one; none -> no_feasible_program.  Comparison is exact
   (Fractions), never on rounded values.
7. Checkpoint "failure probability for one program A delivery opportunity" = 1 - p_A for a SINGLE
   opportunity (not (1-p_A)^3, which would be the probability that all three fail).  Unit "ratio",
   so it is a plain probability.  Returned UNROUNDED; the framework applies half-up to 6 places
   (e.g. 0.5000005 -> 0.500001, 0.6000003 -> 0.600000).  The rounded checkpoint is never fed back
   into the computation: P_eff uses the exact 1 - p_A.
8. The number of opportunities is written as a word ("three").  It is parsed from the text
   (word -> int) rather than hard-coded, in case an instance changes it.
9. Program B's inputs are listed positionally as "corresponding inputs a, b, c, d, and e" in the
   same order as program A's named inputs: fixed cost, unit cost, volume, value per unit,
   probability.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, grab_all, F

TEMPLATE_ID = "h110"

_WORD_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}


def _n_opportunities(text: str) -> int:
    m = re.search(r"exactly\s+(\w+)\s+independent\s+delivery\s+opportunit", text, flags=re.I | re.S)
    if m is None:
        return 3
    token = m.group(1).lower()
    if token in _WORD_NUM:
        return _WORD_NUM[token]
    if token.isdigit():
        return int(token)
    return 3


def _program(fixed: Fraction, unit_cost: Fraction, volume: Fraction, value_per_unit: Fraction,
             p: Fraction, n: int, budget: Fraction, min_volume: Fraction) -> tuple[bool, Fraction, Fraction]:
    total_cost = fixed + unit_cost * volume
    feasible = (total_cost <= budget) and (volume >= min_volume)
    p_eff = Fraction(1) - (Fraction(1) - p) ** n
    planned_value = value_per_unit * volume
    expected_net = planned_value * p_eff - total_cost
    return feasible, expected_net, total_cost


def solve(text: str, q: dict) -> dict:
    # Program A (named inputs)
    fixed_a = grab(r"fixed cost\s+{N}", text)
    unit_cost_a = grab(r"aggregate delivery cost per beneficiary-equivalent unit\s+{N}", text)
    volume_a = grab(r"beneficiary-equivalent volume\s+{N}", text)
    value_a = grab(r"monetized social value per unit\s+{N}", text)
    p_a = grab(r"per-opportunity success probability\s+{N}", text)

    # Program B (positional inputs, same order as A)
    fixed_b, unit_cost_b, volume_b, value_b, p_b = grab_all(
        r"program B with corresponding inputs\s+{N},\s*{N},\s*{N},\s*{N},?\s*and\s+{N}", text
    )

    budget = grab(r"total cost does not exceed\s+{N}", text)
    min_volume = grab(r"volume reaches\s+{N}", text)
    n = _n_opportunities(text)

    feas_a, net_a, _ = _program(fixed_a, unit_cost_a, volume_a, value_a, p_a, n, budget, min_volume)
    feas_b, net_b, _ = _program(fixed_b, unit_cost_b, volume_b, value_b, p_b, n, budget, min_volume)

    if feas_a and feas_b:
        # higher expected net social value wins; exact tie -> program_a
        final = "program_a" if net_a >= net_b else "program_b"
    elif feas_a:
        final = "program_a"
    elif feas_b:
        final = "program_b"
    else:
        final = "no_feasible_program"

    failure_prob_a = Fraction(1) - p_a  # one opportunity of program A fails; unrounded

    return {
        "final": final,
        "slots": {
            "program_a_failure_probability_checkpoint": failure_prob_a,
        },
    }
