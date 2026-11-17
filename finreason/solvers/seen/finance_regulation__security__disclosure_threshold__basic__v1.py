from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.security.disclosure_threshold.basic.v1"


def _bool(flag: bool) -> str:
    return "true" if flag else "false"


def solve(text: str, q: dict) -> dict:
    ownership = grab(r"Ownership percent is {N}", text)
    threshold = grab(r"[Dd]isclosure threshold percent is {N}", text)
    # Signed margin = ownership - threshold (negative when below threshold).
    margin = ownership - threshold
    # "at least the threshold, including equality" -> non-strict; guard a strict variant wording.
    if "strictly" in text and "including equality" not in text:
        required = margin > 0
    else:
        required = margin >= 0
    return {"final": _bool(required), "slots": {"ownership_margin_percent": margin}}
