"""h002: three-state fraud loss, actual expected reimbursement minus flat-rate benchmark.

States (minor, moderate, severe) are mutually exclusive and exhaustive.
  p_minor given; moderate probability is conditional on minor not occurring
  (so unconditional p_mod = (1 - p_minor) * q); severe gets the remainder.
Actual expected reimbursement  = sum p_i * L_i * r_i
Flat-rate benchmark            = (sum p_i * r_i) * (sum p_i * L_i)
Final                          = actual - benchmark
Checkpoints: p_mod * L_mod and p_sev * L_sev (unconditional probability-weighted gross losses).
"""

from fractions import Fraction

from finreason.nums import grab, grab_all

TEMPLATE_ID = "h002"


def solve(text: str, q: dict) -> dict:
    p_minor = grab(r"minor state has probability {N}", text)

    if "minor state not occurring" in text:
        q_mod = grab(r"minor state not occurring, the moderate state has probability {N}", text)
        p_mod = (1 - p_minor) * q_mod
    else:
        p_mod = grab(r"moderate state has probability {N}", text)
    p_sev = 1 - p_minor - p_mod

    losses = grab_all(r"gross fraud losses are {N},? {N},? and {N}", text)
    rates = grab_all(r"reimburses fractions {N},? {N},? and {N}", text)
    assert len(losses) == 3 and len(rates) == 3

    probs = [p_minor, p_mod, p_sev]
    actual = sum((p * l * r for p, l, r in zip(probs, losses, rates)), Fraction(0))
    mean_rate = sum((p * r for p, r in zip(probs, rates)), Fraction(0))
    exp_loss = sum((p * l for p, l in zip(probs, losses)), Fraction(0))
    benchmark = mean_rate * exp_loss

    return {
        "final": actual - benchmark,
        "slots": {
            "moderate_weighted_loss_checkpoint": p_mod * losses[1],
            "severe_weighted_loss_checkpoint": p_sev * losses[2],
        },
    }
