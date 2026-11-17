from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.security.multiple_reporting_thresholds.intermediate.v1"


def _bool(flag: bool) -> str:
    return "true" if flag else "false"


def solve(text: str, q: dict) -> dict:
    ownership = grab(r"Ownership percent is {N}", text)
    value = grab(r"Transaction value in USD is {N}", text)
    own_threshold = grab(r"Ownership threshold percent is {N}", text)
    value_threshold = grab(r"Value threshold in USD is {N}", text)
    # "at least its threshold"; equality triggers each branch (non-strict).
    own_trig = ownership >= own_threshold
    value_trig = value >= value_threshold
    return {
        "final": _bool(own_trig or value_trig),
        "slots": {"ownership_trigger": _bool(own_trig), "value_trigger": _bool(value_trig)},
    }
