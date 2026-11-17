"""h002 -- fraud loss states: actual expected reimbursement minus flat-rate benchmark.

Literal transcription of the question, sentence by sentence.
"""
from fractions import Fraction

from finreason.nums import grab, grab_all, F  # noqa: F401

TEMPLATE_ID = "h002"


def solve(text: str, q: dict) -> dict:
    # S1: "Conditional on one modeled fraud event, exactly one of three mutually exclusive
    #      and exhaustive loss states occurs."  -> probabilities sum to 1.
    # S2: "The minor state has probability {p_minor}."
    p_minor = grab(r"minor state has probability {N}", text)
    # S3: "Conditional on the minor state not occurring, the moderate state has probability
    #      {q_mod}; otherwise the severe state occurs."
    q_mod_given_not_minor = grab(
        r"Conditional on the minor state not occurring, the moderate state has probability {N}", text
    )
    p_not_minor = 1 - p_minor
    p_moderate = p_not_minor * q_mod_given_not_minor
    p_severe = p_not_minor * (1 - q_mod_given_not_minor)
    probs = [p_minor, p_moderate, p_severe]
    assert sum(probs) == 1

    # S4: "Their gross fraud losses are L1, L2, and L3 USD, and the account reimburses
    #      fractions r1, r2, and r3."  (order: minor, moderate, severe)
    losses = grab_all(r"gross fraud losses are {N}, {N},? and {N} USD", text)
    rates = grab_all(r"reimburses fractions {N}, {N},? and {N}", text)
    assert len(losses) == 3 and len(rates) == 3

    # Checkpoints: probability-weighted gross losses per state.
    weighted_loss = [p * L for p, L in zip(probs, losses)]
    moderate_weighted_loss = weighted_loss[1]
    severe_weighted_loss = weighted_loss[2]

    # S5: "Compute actual expected reimbursement across the three states."
    actual_expected_reimbursement = sum(
        (p * r * L for p, r, L in zip(probs, rates, losses)), Fraction(0)
    )

    # S6: "form a scenario-specific flat-rate benchmark by applying the probability-weighted
    #      mean reimbursement rate uniformly to expected gross loss."
    pw_mean_rate = sum((p * r for p, r in zip(probs, rates)), Fraction(0))
    expected_gross_loss = sum(weighted_loss, Fraction(0))
    flat_rate_benchmark = pw_mean_rate * expected_gross_loss

    # S7: "Report actual expected reimbursement minus that benchmark in USD."
    final = actual_expected_reimbursement - flat_rate_benchmark

    return {
        "final": final,
        "slots": {
            "moderate_weighted_loss_checkpoint": moderate_weighted_loss,
            "severe_weighted_loss_checkpoint": severe_weighted_loss,
        },
    }
