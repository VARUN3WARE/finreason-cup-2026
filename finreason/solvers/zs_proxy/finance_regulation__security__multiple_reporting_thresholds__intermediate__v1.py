from fractions import Fraction
from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.security.multiple_reporting_thresholds.intermediate.v1"


def _b(x: bool) -> str:
    return "true" if x else "false"


def solve(text: str, q: dict) -> dict:
    own = grab(r"Ownership percent is {N}", text)
    val = grab(r"Transaction value in USD is {N}", text)
    own_thr = grab(r"Ownership threshold percent is {N}", text)
    val_thr = grab(r"Value threshold in USD is {N}", text)
    own_trig = own >= own_thr  # equality triggers each branch
    val_trig = val >= val_thr
    return {
        "final": _b(own_trig or val_trig),
        "slots": {"ownership_trigger": _b(own_trig), "value_trigger": _b(val_trig)},
    }
