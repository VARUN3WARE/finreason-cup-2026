"""SAR decision: high trigger = score >= high threshold OR (both flags true);
review trigger = score >= medium threshold OR (either flag true);
final = file_sar if high trigger (precedence), else manual_review if review trigger, else no_action.
Triggers are reported as the raw conditions (not suppressed by precedence)."""

import re

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.aml.sar_decision.advanced.v1"


def _flag(pattern: str, text: str) -> bool:
    m = re.search(pattern + r"\s+(true|false)\b", text, flags=re.I | re.S)
    if m is None:
        raise ValueError(f"flag not found: {pattern!r}")
    return m.group(1).lower() == "true"


def _tok(b: bool) -> str:
    return "true" if b else "false"


def solve(text: str, q: dict) -> dict:
    score = grab(r"Base risk score is {N}", text)
    tx = _flag(r"Transaction flag is", text)
    ident = _flag(r"Identity flag is", text)
    medium = grab(r"medium score threshold is {N}", text)
    high = grab(r"high score threshold is {N}", text)
    high_trigger = score >= high or (tx and ident)
    review_trigger = score >= medium or tx or ident
    if high_trigger:
        final = "file_sar"
    elif review_trigger:
        final = "manual_review"
    else:
        final = "no_action"
    return {
        "final": final,
        "slots": {"high_trigger": _tok(high_trigger), "review_trigger": _tok(review_trigger)},
    }
