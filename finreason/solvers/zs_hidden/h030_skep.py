"""Cluster h030 -- fictional remediation budget with a self-reporting credit.

Structure (all 3 instances):
  base assessment B USD; reporting delay of D days at P USD per day;
  fractional credit c applied to the COMBINED (B + D*P); retained fraction r = 1 - c;
  mandatory monitoring cost M USD added OUTSIDE the credit base.
  total = (B + D*P) * (1 - c) + M

AMBIGUITIES CONSIDERED AND HOW THEY WERE RESOLVED (textual evidence in quotes):
 1. Credit is a fraction, not a percent: "Treat 0.2999995 as the fractional credit ...".
    Defensive: if an instance ever says "{N} percent as the fractional credit", divide by 100.
 2. Credit base = combined assessment + delay charge, not the base assessment alone:
    "the fractional credit applied to the combined assessment and delay charge".
    (Applying the factor to each component separately gives the identical result by distributivity.)
 3. Monitoring cost is NOT reduced by the credit: "add mandatory monitoring cost ... outside the credit base",
    and it is added after the credit ("Then add ...").
 4. Delay charge = days * per-day rate, no grace period / threshold / cap is stated, so none is applied.
    A zero-day delay would simply give a zero charge.
 5. Checkpoint post_credit_factor_checkpoint is the retained FRACTION (dimensionless ratio), i.e. 1 - c,
    not the retained USD amount: slot unit is "ratio", description says "the fraction of the combined
    assessment retained after self-reporting credit", and the text says "the retained fraction is one minus
    that rate ... Report the retained-fraction checkpoint independently to six decimal places".
 6. "independently" + "use exact arithmetic through all intermediate steps, round only the final value":
    the UNROUNDED retained fraction feeds the total; the 6-dp display is only for the checkpoint.
    Both are returned unrounded here; the framework applies half-up rounding. Note the instances are
    built so that the checkpoint / total land exactly on a half-way tie (e.g. 0.7000005 -> 0.700001,
    29.715 -> 29.72), which exact Fractions + half-up handle correctly; floats would not.
 7. Units: everything is in plain USD (no millions); the final answer unit is "usd".
 8. Sign: all quantities are positive; no floor at zero is stated, none applied.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h030"


def _credit_fraction(text: str) -> Fraction:
    """Fractional self-reporting credit c (as a ratio), robust to a percent phrasing."""
    m = re.search(
        rf"[Tt]reat\s+({NUMBER})\s*(percent|%)?\s+as\s+the\s+fractional\s+credit",
        text,
        flags=re.S,
    )
    if m is None:
        # fallback: any number immediately preceding "as the fractional credit"
        m = re.search(rf"({NUMBER})\s*(percent|%)?\s+as\s+the\s+fractional\s+credit", text, flags=re.S)
    if m is None:
        raise ValueError("fractional credit not found")
    c = F(m.group(1))
    if m.group(2):
        c = c / 100
    return c


def solve(text: str, q: dict) -> dict:
    base = grab(r"base assessment(?: of)? {N} USD", text)
    days = grab(r"reporting delay of {N} days?", text)
    per_day = grab(r"incurs {N} USD per day", text)
    credit = _credit_fraction(text)
    monitoring = grab(r"monitoring cost(?: of)? {N} USD", text)

    delay_charge = days * per_day                    # USD
    combined = base + delay_charge                   # USD, the credit base
    retained_fraction = Fraction(1) - credit         # ratio (checkpoint, unrounded)
    post_credit = combined * retained_fraction       # USD
    total = post_credit + monitoring                 # USD, monitoring outside the credit base

    return {
        "final": total,
        "slots": {"post_credit_factor_checkpoint": retained_fraction},
    }
