from fractions import Fraction
import re
from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.security.disclosure_threshold.basic.v1"


def solve(text: str, q: dict) -> dict:
    own = grab(r"Ownership percent is {N}", text)
    thr = grab(r"(?:Disclosure )?threshold percent is {N}", text)
    margin = own - thr
    # Default rule: required when ownership is at least threshold (equality included).
    # Detect a strict-inequality variant if the wording says so.
    strict = bool(re.search(r"strictly (?:greater|above|exceeds)|excluding equality|equality does not", text, re.I))
    if strict:
        required = own > thr
    else:
        required = own >= thr
    return {"final": "true" if required else "false", "slots": {"ownership_margin_percent": margin}}
