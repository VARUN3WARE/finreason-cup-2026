"""Cluster h089 -- fictional KYC control-credit policy: minimum additional verified-control credit.

AMBIGUITY RESOLUTIONS (skeptical pass, all resolved from the question text):

A1. What the checkpoint "combined source-of-funds and jurisdiction risk score" denotes.
    Candidates: (a) sof + jur (gross, before any credit); (b) sof + jur - existing credit (net).
    Resolution: (a). The slot description names only the two scores, and the question body
    defines the quantity verbatim as "the source-of-funds score plus the jurisdiction score"
    before saying "less existing and additional credit". The credits are a separate step.

A2. Strict vs non-strict comparison.
    "no greater than the residual-risk ceiling" => residual <= ceiling (non-strict). The minimum
    additional credit therefore brings residual exactly to the ceiling: no epsilon is added.

A3. Floor at zero.
    "additional credit cannot be negative" => additional = max(0, sof + jur - existing - ceiling).
    If the existing credit alone already satisfies the ceiling, the answer is 0 (branch may differ
    across instances; implemented generically, never assumed positive).

A4. How credits apply.
    "Existing and additional verified-control credit each reduce residual risk one-for-one" and
    "All four values use the same additive risk-point scale" => credits are subtracted additively
    from the sum (not a percentage reduction, not applied to one score only).

A5. Rounding inside the computation.
    No sentence says a rounded or whole-unit value is reused downstream, so every value is exact
    Fraction arithmetic; the framework applies half-up 2dp rendering to the final and the slot.

A6. Units.
    Everything is in dimensionless risk-score points; nothing is a percent; no unit conversion.

A7. Could "existing credit" already be netted into the stated scores?
    No: the question states the formula explicitly as (sof + jur) - existing - additional, and
    the scores are introduced as raw "risk score" values, so existing credit is subtracted once.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h089"


def _grab_any(patterns: list[str], text: str) -> Fraction:
    """Try several anchored patterns in order; raise if none match."""
    last_err: Exception | None = None
    for p in patterns:
        try:
            return grab(p, text)
        except ValueError as exc:  # pattern not found
            last_err = exc
    raise ValueError(f"none of the patterns matched: {patterns!r}") from last_err


# Tolerate hyphen/space variants ("source-of-funds", "source of funds", "risk score", "risk-score")
# and an optional "of" before the number.
_SEP = r"[\s-]+"
_SCORE = r"risk" + _SEP + r"score(?:\s+of)?\s+"


def solve(text: str, q: dict) -> dict:
    sof = _grab_any(
        [
            r"source" + _SEP + r"of" + _SEP + r"funds" + _SEP + _SCORE + r"{N}",
            r"source" + _SEP + r"of" + _SEP + r"funds[^.,;]*?\s{N}",
        ],
        text,
    )
    jur = _grab_any(
        [
            r"jurisdiction" + _SEP + _SCORE + r"{N}",
            r"jurisdiction[^.,;]*?\s{N}",
        ],
        text,
    )
    existing = _grab_any(
        [
            r"existing" + _SEP + r"verified" + _SEP + r"control" + _SEP + r"credit(?:\s+of)?\s+{N}",
            r"existing[^.,;]*?credit(?:\s+of)?\s+{N}",
        ],
        text,
    )
    ceiling = _grab_any(
        [
            r"residual" + _SEP + r"risk" + _SEP + r"ceiling(?:\s+of)?\s+{N}",
            r"ceiling(?:\s+of)?\s+{N}",
        ],
        text,
    )

    # A1: checkpoint = gross combined score, before any credit.
    combined = sof + jur

    # A2/A3/A4: residual = combined - existing - additional <= ceiling, additional >= 0, minimise.
    shortfall = combined - existing - ceiling
    additional = shortfall if shortfall > 0 else Fraction(0)

    return {
        "final": additional,
        "slots": {"combined_risk_checkpoint": combined},
    }
