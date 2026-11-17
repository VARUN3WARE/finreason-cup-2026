"""h110 -- social-impact program A vs B, each with independent repeated delivery opportunities.

Literal transcription of the question, sentence by sentence:

 1. Program A inputs (fixed cost, aggregate delivery cost per beneficiary-equivalent unit,
    beneficiary-equivalent volume, monetized social value per unit, per-opportunity success
    probability); program B gives the "corresponding inputs" in the same order.
 2. total cost = fixed cost + aggregate per-unit delivery cost * volume.
 3. Each program has exactly N (three) independent delivery opportunities sharing its
    per-opportunity probability.
 4. The stated total cost covers all opportunities (no multiplication by N); the planned social
    value is realized once if at least one opportunity succeeds.
 5. effective delivery probability = 1 - (probability one opportunity fails) ** N.
 6. expected net social value = planned monetized social value * effective probability - total cost,
    where planned monetized social value = social value per unit * volume.
 7. feasible  <=>  total cost <= budget ("does not exceed")  and  volume >= minimum ("reaches").
 8. Both feasible -> higher expected net social value, tie -> program_a; exactly one feasible ->
    that one; none -> no_feasible_program.

Checkpoint: failure probability for ONE program A delivery opportunity = 1 - p_A (ratio).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import F, grab, grab_all

TEMPLATE_ID = "h110"

_WORD_COUNTS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _count(token: str) -> int:
    t = token.strip().lower()
    if t in _WORD_COUNTS:
        return _WORD_COUNTS[t]
    return int(t)


def solve(text: str, q: dict) -> dict:
    # --- Sentence 1: program A inputs, then program B's corresponding inputs (same order).
    fixed_cost_a = grab(r"program A, with fixed cost {N}", text)
    unit_delivery_cost_a = grab(r"aggregate delivery cost per beneficiary-equivalent unit {N}", text)
    volume_a = grab(r"beneficiary-equivalent volume {N}", text)
    social_value_per_unit_a = grab(r"monetized social value per unit {N}", text)
    success_prob_a = grab(r"per-opportunity success probability {N}", text)
    (
        fixed_cost_b,
        unit_delivery_cost_b,
        volume_b,
        social_value_per_unit_b,
        success_prob_b,
    ) = grab_all(r"program B with corresponding inputs {N},\s*{N},\s*{N},\s*{N},\s*and {N}", text)

    for p in (success_prob_a, success_prob_b):
        if not (Fraction(0) <= p <= Fraction(1)):
            raise ValueError(f"per-opportunity probability out of range: {p}")

    # --- Sentence 3: exactly N independent delivery opportunities per program.
    m = re.search(r"exactly (\w+) independent delivery opportunities", text)
    if m is None:
        raise ValueError("number of delivery opportunities not found")
    n_opportunities = _count(m.group(1))

    # --- Sentence 7: feasibility thresholds.
    budget = grab(r"total cost does not exceed {N}", text)
    min_volume = grab(r"its volume reaches {N}", text)

    def evaluate(fixed_cost, unit_delivery_cost, volume, social_value_per_unit, success_prob):
        # Sentence 2: total cost = fixed cost + aggregate per-unit delivery cost * volume.
        total_cost = fixed_cost + unit_delivery_cost * volume
        # Sentence 4: total cost covers all opportunities; planned value realized once.
        planned_social_value = social_value_per_unit * volume
        # Sentence 5: effective delivery probability = 1 - P(all opportunities fail).
        failure_prob_one = 1 - success_prob
        prob_all_fail = failure_prob_one ** n_opportunities
        effective_prob = 1 - prob_all_fail
        # Sentence 6: expected net social value.
        expected_net_social_value = planned_social_value * effective_prob - total_cost
        # Sentence 7: feasible only when total cost does not exceed budget and volume reaches minimum.
        feasible = (total_cost <= budget) and (volume >= min_volume)
        return {
            "total_cost": total_cost,
            "planned_social_value": planned_social_value,
            "failure_prob_one": failure_prob_one,
            "effective_prob": effective_prob,
            "ensv": expected_net_social_value,
            "feasible": feasible,
        }

    a = evaluate(fixed_cost_a, unit_delivery_cost_a, volume_a, social_value_per_unit_a, success_prob_a)
    b = evaluate(fixed_cost_b, unit_delivery_cost_b, volume_b, social_value_per_unit_b, success_prob_b)

    # --- Sentence 8: selection rule.
    if a["feasible"] and b["feasible"]:
        final = "program_a" if a["ensv"] >= b["ensv"] else "program_b"  # tie -> program_a
    elif a["feasible"]:
        final = "program_a"
    elif b["feasible"]:
        final = "program_b"
    else:
        final = "no_feasible_program"

    return {
        "final": final,
        "slots": {
            # Failure probability for one program A delivery opportunity (ratio), unrounded.
            "program_a_failure_probability_checkpoint": a["failure_prob_one"],
        },
    }
