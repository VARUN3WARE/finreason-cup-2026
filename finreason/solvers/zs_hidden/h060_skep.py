"""h060 -- fictional customer-review policy: risk-score migration + flag overrides.

Ambiguities hunted and resolved (textual evidence in quotes):

A1. Strict vs non-strict comparisons.
    "Use Enhanced review when that signed migration REACHES the positive
    material-migration threshold or current risk REACHES the elevated-current-risk
    threshold". "Reaches" = attains = non-strict:  migration >= M  or  current >= E.
    Equality triggers Enhanced review.

A2. Signed vs absolute migration.
    "Compute SIGNED score migration as current risk score minus prior risk score"
    and the trigger is "reaches the POSITIVE material-migration threshold".
    => compare the signed value (current - prior) against +M. A large negative
    migration (score dropping) does NOT trigger Enhanced review. We do not take abs().

A3. Order of precedence of the overrides.
    "Stale documentation overrides THAT RESULT [Enhanced review / Routine monitoring]
    with Suspend and refresh records, while suspicious activity has HIGHEST
    precedence and produces Restrict and investigate."
    => suspicious activity  >  stale documentation  >  (Enhanced review | Routine monitoring).
    Suspicious activity wins even when stale documentation is also true.

A4. Checkpoint quantity and unit.
    Slot risk_migration_checkpoint: "signed current risk score minus prior risk score",
    dimensionless, half-up to 2 dp (applied by the framework). It is reported
    UNROUNDED and is computed regardless of which label finally wins
    (the override labels do not remove the slot).

A5. Boolean flags.
    "reports suspicious activity false and stale documentation true" -- literal
    true/false tokens immediately following the flag name. Parsed case-insensitively;
    yes/no tolerated as synonyms for robustness. Anything else raises.

A6. Which base each threshold applies to.
    material-migration threshold  -> compared with the migration (current - prior).
    elevated-current-risk threshold -> compared with the CURRENT risk score alone
    ("current risk reaches the elevated-current-risk threshold").

A7. No rounding anywhere inside the computation: thresholds are compared with the
    exact (Fraction) migration, never with the 2-dp displayed checkpoint.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h060"

_ROUTINE = "Routine monitoring"
_ENHANCED = "Enhanced review"
_SUSPEND = "Suspend and refresh records"
_RESTRICT = "Restrict and investigate"

# Tolerant connector between a label and its number: "is", "of", "=", ":" or nothing.
_IS = r"\s*(?:is|of|=|:|equals)?\s*"


def _num(label_pattern: str, text: str) -> Fraction:
    return grab(label_pattern + _IS + "{N}", text)


def _flag(label_pattern: str, text: str) -> bool:
    m = re.search(
        label_pattern + r"\s*(?:is|=|:|reported(?:\s+as)?)?\s*(true|false|yes|no)\b",
        text,
        flags=re.I | re.S,
    )
    if m is None:
        raise ValueError(f"flag not found: {label_pattern!r}")
    return m.group(1).lower() in ("true", "yes")


def solve(text: str, q: dict) -> dict:
    prior = _num(r"prior\s+risk\s+score", text)
    current = _num(r"current\s+risk\s+score", text)
    mat_thr = _num(r"material[-\s]+migration\s+threshold", text)
    elev_thr = _num(r"elevated[-\s]+current[-\s]+risk\s+threshold", text)

    suspicious = _flag(r"suspicious\s+activity", text)
    stale = _flag(r"stale\s+documentation", text)

    # A2/A4: signed migration, exact.
    migration = current - prior

    # A1/A6: non-strict "reaches" on both triggers.
    enhanced = (migration >= mat_thr) or (current >= elev_thr)
    base = _ENHANCED if enhanced else _ROUTINE

    # A3: precedence suspicious > stale > base.
    if suspicious:
        final = _RESTRICT
    elif stale:
        final = _SUSPEND
    else:
        final = base

    return {"final": final, "slots": {"risk_migration_checkpoint": migration}}
