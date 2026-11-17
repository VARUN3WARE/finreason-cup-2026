"""Hidden cluster h102 -- additional stake in a second DeFi pool to reach a net annual reward.

Structure (one annual period, simple yield, no compounding):
    existing_reward = P1 * r1                      (gross reward of the position the user already has)
    net_reward      = existing_reward + X * r2 - fee
    solve net_reward == R  ->  X = (R + fee - existing_reward) / r2

AMBIGUITY HUNT (two competent analysts could disagree) and resolutions:

 1. Scope of "net annual reward of R USD": is R the net reward of the WHOLE account (existing position
    + new stake - fee) or of the new stake alone (X*r2 - fee)?
    -> WHOLE account. The text deliberately states the existing principal and its yield ratio, and the
       graded checkpoint is "the reward supplied by the existing position", which would be irrelevant if
       only the new stake counted. Hence R = P1*r1 + X*r2 - fee.

 2. "yield ratio 0.1" / "yield ratio 1/7": ratio vs percent.
    -> Plain ratio (0.1 = 10%). The word is "ratio", and one instance gives it as the rational 1/7.
       No division by 100.  (A defensive fallback divides by 100 only if the text literally says "percent".)

 3. Compounding / period count: "Over one annual period" with annual yield ratios -> a single simple
    period; reward = principal * ratio. No compounding, no scaling of rates.

 4. Fee treatment: "fixed annual fee of F USD that does not depend on the added principal".
    -> One constant subtraction from the gross reward of the period (not proportional to X, not
       proportional to the total principal, not split between pools). Being "net", the target reward is
       after this fee, so the fee is ADDED back when solving for X.

 5. Checkpoint "reward supplied by the existing position": gross (P1*r1) or net of the fee?
    -> GROSS. The fee is a protocol charge, not something the position "supplies"; the position supplies
       P1*r1 USD. Unit USD, rendered to 4 dp by the framework (unrounded value returned).

 6. Sign / floor at zero: no floor or max(0, .) is stated, so the raw solution is returned. (All three
    instances require a strictly positive additional stake anyway, so no branch is exercised.)

 7. Rounding: "use exact arithmetic through all intermediate steps, round only the final value" ->
    no intermediate rounding; the displayed 4-dp checkpoint is never fed back into the chain.
    Everything is Fraction; the final X is returned unrounded (framework rounds half-up to 2 dp).
"""

from __future__ import annotations

from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h102"


def _ratio(pattern_ratio: str, pattern_pct: str, text: str, group: int = 1) -> Fraction:
    """Yield given as a plain ratio (expected); divide by 100 only if literally phrased in percent."""
    try:
        return grab(pattern_ratio, text, group=group)
    except ValueError:
        return grab(pattern_pct, text, group=group) / 100


def solve(text: str, q: dict) -> dict:
    # Existing position: principal (group 1) and its yield ratio (group 2 of the same anchored match).
    p1 = grab(r"already has\s+{N}\s+USD", text)
    r1 = _ratio(
        r"already has\s+{N}\s+USD\s+earning\s+(?:a\s+)?yield\s+ratio\s+(?:of\s+)?{N}",
        r"already has\s+{N}\s+USD\s+earning\s+(?:a\s+)?yield\s+(?:of\s+)?{N}\s*percent",
        text,
        group=2,
    )

    # Second pool yield ratio.
    r2 = _ratio(
        r"second pool offers\s+(?:a\s+)?yield\s+ratio\s+(?:of\s+)?{N}",
        r"second pool offers\s+(?:a\s+)?yield\s+(?:of\s+)?{N}\s*percent",
        text,
    )

    # Fixed annual protocol fee (USD) and the target net annual reward (USD).
    fee = grab(r"fixed annual fee of\s+{N}\s+USD", text)
    target = grab(r"net annual reward of\s+{N}\s+USD", text)

    # Chain.
    existing_reward = p1 * r1                      # checkpoint: gross reward of the existing position
    needed_from_new = target + fee - existing_reward  # X * r2 must supply this
    stake = needed_from_new / r2

    return {
        "final": stake,
        "slots": {"existing_reward_checkpoint": existing_reward},
    }
