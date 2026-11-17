"""Hidden cluster h017 -- joint vs alternative stress scenario, capital adequacy check.

AMBIGUITY RESOLUTIONS (recorded before implementation):

A1. "their product times k contributes an interaction rate" -- "their" refers to the compound
    subject of the sentence (market shock ratio ... and credit shock ratio ...), so the
    interaction rate is k * market_shock * credit_shock: the standard second-order cross term
    of a stress-test loss expansion.  It is NOT the product of the two linear loss rates
    (shock*sensitivity each).  Supporting evidence: with this reading the instance whose
    coefficient is 1.00895 yields a joint ratio with exactly 6 decimals (1.00895*0.04 =
    0.040358), matching the checkpoint's 6-decimal half-up spec; the other reading gives 8.
A2. "market shock ratio s with sensitivity b ... contribute linear loss rates" -- each linear
    loss rate is shock * sensitivity (shock ratios are already ratios, not percents).
A3. Checkpoint "total joint-scenario loss ratio" -- the full joint rate (both linear terms plus
    the interaction term), as a dimensionless ratio, BEFORE conversion to dollars.
A4. Alternative scenario "shock ratio s is squared and multiplied by m" -- alt_rate = s**2 * m
    (square first, then multiply; not (s*m)**2).
A5. "Convert each scenario rate to a dollar loss" -- rate * portfolio worth (loss rates apply
    to the portfolio value, not to the available capital).
A6. "use the larger loss" -- max of the two dollar losses; a tie gives the same loss either way.
A7. "subtract it from available capital ... capital_pass when the remaining capital meets the
    minimum" -- remaining = capital - loss (may be negative, no floor); pass iff
    remaining >= minimum ("meets" / "at least" are non-strict).
A8. No rounding anywhere inside the chain; all values returned exact.
"""

from __future__ import annotations

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h017"


def solve(text: str, q: dict) -> dict:
    worth = grab(r"portfolio worth {N}", text)
    capital = grab(r"available capital {N}", text)
    minimum = grab(r"must retain at least {N}", text)

    m_shock = grab(r"market shock ratio {N}", text)
    m_sens = grab(r"market shock ratio {N} with sensitivity {N}", text, group=2)
    c_shock = grab(r"credit shock ratio {N}", text)
    c_sens = grab(r"credit shock ratio {N} with sensitivity {N}", text, group=2)
    inter_coef = grab(r"their product times {N}", text)

    alt_shock = grab(r"alternative scenario, shock ratio {N}", text)
    alt_mult = grab(r"is squared and multiplied by {N}", text)

    # A1/A2/A3: joint-scenario total loss ratio
    linear_rate = m_shock * m_sens + c_shock * c_sens
    interaction_rate = inter_coef * m_shock * c_shock
    joint_rate = linear_rate + interaction_rate

    # A4: alternative scenario loss ratio
    alt_rate = alt_shock ** 2 * alt_mult

    # A5: dollar losses on the portfolio value
    joint_loss = joint_rate * worth
    alt_loss = alt_rate * worth

    # A6: larger loss
    loss = joint_loss if joint_loss >= alt_loss else alt_loss

    # A7: remaining capital vs minimum (non-strict)
    remaining = capital - loss
    final = "capital_pass" if remaining >= minimum else "capital_fail"

    return {
        "final": final,
        "slots": {"joint_rate_checkpoint": Fraction(joint_rate)},
    }
