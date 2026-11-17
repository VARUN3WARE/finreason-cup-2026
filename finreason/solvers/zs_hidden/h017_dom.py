"""h017 -- capital adequacy under a joint (two-factor) stress scenario vs. a single-factor alternative.

FINANCE MODEL (written before coding)
-------------------------------------
Inputs: portfolio value V, available capital C, minimum retained capital M.
Joint scenario: market shock x with loss sensitivity a, credit shock y with loss sensitivity b, interaction
coefficient k.
  linear loss rate (market) = a * x          (sensitivity times shock ratio: a loss rate per unit of portfolio)
  linear loss rate (credit) = b * y
  interaction rate          = k * (x * y)    ("their product" = product of the two SHOCK ratios, times k;
                                              this matches the sibling public template "joint effect is the product
                                              of both shocks and <coefficient>")
  total joint loss rate     = a*x + b*y + k*x*y        <-- checkpoint joint_rate_checkpoint (ratio, unrounded)
Alternative scenario: shock ratio s, squared, times multiplier m:  alt rate = m * s^2.
Dollar loss for each scenario = V * rate (rate is a fraction of portfolio value).
Binding loss = max(joint loss, alt loss)   (larger loss; ties irrelevant for max).
Remaining capital = C - binding loss.
Answer: capital_pass if remaining >= M ("meets the minimum" => at least, non-strict), else capital_fail.

Conventions / overrides: none; all arithmetic exact Fractions; nothing is rounded inside the computation.
Ambiguity resolved: "their product" -> product of the shock ratios (not of the two linear loss rates).
(For the 3 known instances the pass/fail answer is identical under either reading.)
"""
from fractions import Fraction
from finreason.nums import grab, after, before, numbers, grab_all, F

TEMPLATE_ID = "h017"


def solve(text: str, q: dict) -> dict:
    V = grab(r"portfolio worth {N}", text)
    C = grab(r"available capital {N}", text)
    M = grab(r"must retain at least {N}", text)
    x, a = grab_all(r"market shock ratio {N} with sensitivity {N}", text)
    y, b = grab_all(r"credit shock ratio {N} with sensitivity {N}", text)
    k = grab(r"their product times {N}", text)
    s = grab(r"alternative scenario, shock ratio {N} is squared", text)
    m = grab(r"squared and multiplied by {N}", text)

    joint_rate = a * x + b * y + k * x * y
    alt_rate = m * s ** 2
    joint_loss = V * joint_rate
    alt_loss = V * alt_rate
    loss = max(joint_loss, alt_loss)
    remaining = C - loss
    final = "capital_pass" if remaining >= M else "capital_fail"
    return {"final": final, "slots": {"joint_rate_checkpoint": joint_rate}}
