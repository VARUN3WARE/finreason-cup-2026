"""h010 -- required joint success probability of two post-merger initiatives, placed in the Frechet band.

Literal transcription of the question text, sentence by sentence.
"""
from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h010"


def solve(text: str, q: dict) -> dict:
    # "The cost-synergy initiative has marginal success probability P and contributes B USD millions whenever it succeeds."
    p_cost, b_cost = grab_all(
        r"cost-synergy initiative has marginal success probability {N} and contributes {N} USD millions", text
    )
    # "The revenue-synergy initiative has marginal success probability P and contributes B USD millions whenever it succeeds."
    p_rev, b_rev = grab_all(
        r"revenue-synergy initiative has marginal success probability {N} and contributes {N} USD millions", text
    )
    # "the cost-synergy probability is strictly higher than the revenue-synergy probability and their sum exceeds one."
    assert p_cost > p_rev and p_cost + p_rev > 1, "ordered-marginal premise violated"
    # "If both initiatives succeed, incremental benefit X USD millions is earned beyond the standalone benefits."
    incr = grab(r"incremental benefit {N} USD millions", text)
    # "Unconditional integration cost is K USD millions"
    cost = grab(r"[Uu]nconditional integration cost is {N} USD millions", text)
    # "required expected net benefit is T USD millions"
    target = grab(r"required expected net benefit is {N} USD millions", text)

    # Expected net benefit = p_cost*b_cost + p_rev*b_rev + p_joint*incr - cost  (linear in p_joint; no
    # dependence structure needed beyond the joint probability itself).
    # Checkpoint 1: gross expected benefit required before the integration cost is deducted.
    gross_required = target + cost
    standalone = p_cost * b_cost + p_rev * b_rev
    # "Solve for the joint success probability needed to meet the target."
    p_joint = (gross_required - standalone) / incr

    # "The Frechet lower bound is the revenue-synergy probability minus the cost-synergy failure probability,
    #  the upper bound is the revenue-synergy probability, and the band width is the cost-synergy failure probability."
    cost_fail = 1 - p_cost
    lower = p_rev - cost_fail
    upper = p_rev
    width = cost_fail
    assert upper - lower == width

    # "Report the percentage of this feasible band consumed above its lower bound by the required joint success
    #  probability." 0% = lower bound, 100% = upper bound, >100% infeasible (reported as is, not clamped).
    pct_band = (p_joint - lower) / width * 100

    return {
        "final": pct_band,
        "slots": {
            "gross_requirement_checkpoint": gross_required,
            "frechet_lower_bound_checkpoint": lower,
        },
    }
