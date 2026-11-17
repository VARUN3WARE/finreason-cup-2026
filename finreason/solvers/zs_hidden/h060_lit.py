"""h060 -- fictional customer risk-review policy (literal transcription).

Sentence-by-sentence:
  1. prior risk score, current risk score, material-migration threshold,
     elevated-current-risk threshold.
  2. suspicious activity flag, stale documentation flag.
  3. signed score migration = current risk score - prior risk score.
  4. Enhanced review when migration reaches (>=) the positive material-migration
     threshold OR current risk reaches (>=) the elevated-current-risk threshold;
     otherwise Routine monitoring.
  5. Stale documentation overrides that result -> Suspend and refresh records;
     suspicious activity has highest precedence -> Restrict and investigate.
"""

import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h060"

_TRUE = {"true", "yes", "y", "1"}
_FALSE = {"false", "no", "n", "0"}


def _flag(name: str, text: str) -> bool:
    m = re.search(name + r"\s*(?:flag\s*)?(?:is\s*|=\s*|:\s*)?(true|false|yes|no)\b",
                  text, flags=re.I)
    if m is None:
        raise ValueError(f"flag not found: {name}")
    tok = m.group(1).lower()
    if tok in _TRUE:
        return True
    if tok in _FALSE:
        return False
    raise ValueError(f"bad flag token {tok!r} for {name}")


def solve(text: str, q: dict) -> dict:
    # Sentence 2: scores and thresholds.
    prior = grab(r"prior risk score is {N}", text)
    current = grab(r"current risk score is {N}", text)
    material_threshold = grab(r"material-migration threshold is {N}", text)
    elevated_threshold = grab(r"elevated-current-risk threshold is {N}", text)

    # Sentence 3: review flags.
    suspicious = _flag(r"suspicious activity", text)
    stale = _flag(r"stale documentation", text)

    # Sentence 4: signed migration.
    signed_migration = current - prior

    # Sentence 5: base result ("reaches" = at least; positive threshold, signed migration).
    positive_material_threshold = abs(material_threshold)
    if signed_migration >= positive_material_threshold or current >= elevated_threshold:
        label = "Enhanced review"
    else:
        label = "Routine monitoring"

    # Sentence 6: overrides, suspicious activity has highest precedence.
    if stale:
        label = "Suspend and refresh records"
    if suspicious:
        label = "Restrict and investigate"

    return {
        "final": label,
        "slots": {"risk_migration_checkpoint": Fraction(signed_migration)},
    }
