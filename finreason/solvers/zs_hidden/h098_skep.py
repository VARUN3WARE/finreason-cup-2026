"""h098 -- maximum risky-asset weight under a stress floor and a policy cap.

Structure (shared by all 3 instances):
    V  = current portfolio value            ("portfolio worth V")
    L  = stressed-value floor               ("remain at or above L", with L < V)
    d  = fraction of the risky allocation lost in the stress scenario
         ("loses d of its allocated amount")
    c  = policy cap on the risky-asset weight ("caps ... weight at c")

    Stressed value with weight w:  V - d * (w * V)     (non-risky capital keeps its value)
    Floor:                          V - d*w*V >= L  <=>  w <= (V - L) / (d * V)
    Max permitted weight:           w* = min( (V - L) / (d * V), c )
    Final answer:                   w* * 100  (percent, framework rounds half-up 2dp)
    Checkpoint loss_budget_checkpoint: V - L  (USD, the allowable dollar loss under the floor)

Ambiguities considered and how they were resolved (skeptical pass):
 1. "loses 0.3 of its allocated amount": a FRACTION of the risky allocation (0.3 = 30%),
    not a percent figure -- "0.3 of" is multiplicative wording and every instance uses a value < 1.
 2. Policy cap "at 0.25": a fractional weight (0.25 = 25%), consistent with the request to
    report the weight "as a percentage", i.e. weight * 100.
 3. "at or above L": NON-strict floor, so the stress-implied maximum weight is exactly
    (V - L) / (d V), attained with equality -- no epsilon, no strict-inequality adjustment.
 4. Cap "at c": NON-strict as well (w <= c); max permitted = min(stress weight, c).
 5. The two constraints are applied to the UNROUNDED exact weight (text says so explicitly);
    rounding to 2 dp of the percentage is reporting only -> we return the exact Fraction and
    let the framework round. No intermediate rounding anywhere.
 6. Checkpoint "allowable dollar loss under the floor" = loss budget = V - L (slot id
    loss_budget_checkpoint), NOT the stressed loss at the chosen weight (d*w*V) and NOT the
    loss implied by the cap. It is positive because L is "strictly below" V. Unit: USD.
 7. The loss fraction applies to the risky asset's allocated AMOUNT (w*V), and "all capital
    outside the risky asset retains its value" -> stressed value = V - d*w*V, linear in w.
 8. No floor at zero / cap at 1 is needed: L < V guarantees the stress weight is > 0, and the
    text names only the stress floor and the policy cap as the operative constraints.
 9. Base of the weight: "portfolio weight" = fraction of the CURRENT portfolio value V (not of
    the stressed value), so the allocated amount is w*V.
"""

from __future__ import annotations

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h098"


def _grab_first(patterns: list[str], text: str) -> Fraction:
    last_err: Exception | None = None
    for p in patterns:
        try:
            return grab(p, text)
        except ValueError as e:  # pragma: no cover - fallthrough to next pattern
            last_err = e
    raise ValueError(f"none of the patterns matched: {patterns!r}") from last_err


def solve(text: str, q: dict) -> dict:
    # Current portfolio value V.
    V = _grab_first(
        [
            r"portfolio worth\s+(?:USD\s+|\$\s*)?{N}",
            r"portfolio (?:valued at|value of|of)\s+(?:USD\s+|\$\s*)?{N}",
        ],
        text,
    )
    # Stress floor L (stressed value must remain at or above L).
    L = _grab_first(
        [
            r"at or above\s+(?:USD\s+|\$\s*)?{N}",
            r"no (?:lower|less) than\s+(?:USD\s+|\$\s*)?{N}",
        ],
        text,
    )
    # Fraction of the risky allocation lost under stress.
    d = _grab_first(
        [
            r"risky asset loses\s+{N}\s+of its allocated amount",
            r"loses\s+{N}\s+of its allocated",
            r"loses\s+{N}\s+of",
        ],
        text,
    )
    # Policy cap on the risky-asset weight (fraction).
    c = _grab_first(
        [
            r"caps the risky asset's portfolio weight at\s+{N}",
            r"caps the risky[- ]asset(?:'s)? (?:portfolio )?weight at\s+{N}",
            r"weight at\s+{N}",
        ],
        text,
    )

    if V <= 0 or d <= 0:
        raise ValueError("portfolio value and stress loss fraction must be positive")

    # Checkpoint: allowable dollar loss before the floor is breached.
    loss_budget = V - L

    # Stress-implied maximum weight: V - d*w*V >= L  <=>  w <= (V - L) / (d V).
    w_stress = loss_budget / (d * V)

    # Policy cap applied to the exact (unrounded) stress weight.
    w_max = min(w_stress, c)

    return {
        "final": w_max * 100,  # percent
        "slots": {"loss_budget_checkpoint": loss_budget},
    }
