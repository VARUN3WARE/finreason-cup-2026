"""h060: customer risk-score migration review policy (enum label + signed migration checkpoint)."""

import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h060"

_TRUE = {"true", "yes", "y", "1"}
_FALSE = {"false", "no", "n", "0"}


def _flag(name: str, text: str) -> bool:
    m = re.search(name + r"\s*(?:flag\s*)?(?:is\s*|=\s*|:\s*)?(true|false|yes|no)\b", text, flags=re.I)
    if m is None:
        raise ValueError(f"flag not found: {name}")
    v = m.group(1).lower()
    if v in _TRUE:
        return True
    if v in _FALSE:
        return False
    raise ValueError(f"bad flag value {v!r} for {name}")


def solve(text: str, q: dict) -> dict:
    prior = grab(r"prior risk score (?:is|of|=)?\s*{N}", text)
    current = grab(r"current risk score (?:is|of|=)?\s*{N}", text)
    mig_thr = grab(r"material-migration threshold (?:is|of|=)?\s*{N}", text)
    elev_thr = grab(r"elevated-current-risk threshold (?:is|of|=)?\s*{N}", text)
    suspicious = _flag(r"suspicious activity", text)
    stale = _flag(r"stale documentation", text)

    migration = Fraction(current) - Fraction(prior)

    # "reaches" = at least (>=); migration is signed, so only upward migration can reach it.
    if migration >= mig_thr or current >= elev_thr:
        label = "Enhanced review"
    else:
        label = "Routine monitoring"
    if stale:
        label = "Suspend and refresh records"
    if suspicious:  # highest precedence
        label = "Restrict and investigate"

    return {"final": label, "slots": {"risk_migration_checkpoint": migration}}
