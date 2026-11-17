# FINANCE MODEL (h060): fictional scenario-local customer risk-review policy (KYC / AML style triage).
#
# Inputs
#   prior   = prior risk score            (dimensionless score)
#   cur     = current risk score          (dimensionless score)
#   m_thr   = material-migration threshold (positive, in score points)
#   e_thr   = elevated-current-risk threshold (score level)
#   susp    = suspicious activity flag (true/false)
#   stale   = stale documentation flag (true/false)
#
# Quantity
#   migration = cur - prior   (SIGNED: a decline in risk gives a negative migration; no abs value, no rounding)
#   Checkpoint 1 (risk_migration_checkpoint) = migration, reported at 2 dp half-up by the framework.
#
# Decision cascade (precedence low -> high; each later rule OVERRIDES the earlier result)
#   1. base = "Enhanced review" if (migration >= m_thr  [and migration > 0, "positive" threshold])
#                                  or (cur >= e_thr)
#             else "Routine monitoring".
#      "reaches" = at least (>=), i.e. equality triggers.  Only an UPWARD move counts as material
#      migration: a large negative migration (improvement) never triggers, because the threshold is the
#      *positive* material-migration threshold.
#   2. stale documentation true  -> "Suspend and refresh records"  (overrides step 1)
#   3. suspicious activity true  -> "Restrict and investigate"     (highest precedence, overrides all)
#
# Overrides of standard conventions: none. Scores/thresholds are taken at face value (exact Fractions);
# nothing is rounded inside the computation (checkpoint is independently rounded by the framework).

import re
from fractions import Fraction

from finreason.nums import grab, F  # noqa: F401

TEMPLATE_ID = "h060"


def _flag(label: str, text: str) -> bool:
    m = re.search(label + r"\s+(true|false)\b", text, flags=re.I)
    if m is None:
        raise ValueError(f"flag not found: {label!r}")
    return m.group(1).lower() == "true"


def solve(text: str, q: dict) -> dict:
    prior = grab(r"prior risk score is {N}", text)
    cur = grab(r"current risk score is {N}", text)
    m_thr = grab(r"material-migration threshold is {N}", text)
    e_thr = grab(r"elevated-current-risk threshold is {N}", text)

    susp = _flag(r"suspicious activity", text)
    stale = _flag(r"stale documentation", text)

    migration = cur - prior  # signed

    material = migration > 0 and migration >= m_thr
    elevated = cur >= e_thr

    if material or elevated:
        decision = "Enhanced review"
    else:
        decision = "Routine monitoring"

    if stale:
        decision = "Suspend and refresh records"
    if susp:
        decision = "Restrict and investigate"

    return {"final": decision, "slots": {"risk_migration_checkpoint": migration}}
