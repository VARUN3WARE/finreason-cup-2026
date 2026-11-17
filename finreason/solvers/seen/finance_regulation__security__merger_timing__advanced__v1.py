import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.security.merger_timing.advanced.v1"


def _bool(flag: bool) -> str:
    return "true" if flag else "false"


def solve(text: str, q: dict) -> dict:
    event_day = grab(r"Event day offset is {N}", text)
    disclosure_day = grab(r"Disclosure day offset is {N}", text)
    allowance = grab(r"Allowed delay in whole days is {N}", text)
    m = re.search(r"Leak flag is (true|false)", text, flags=re.I)
    if m is None:
        raise ValueError("leak flag not found")
    leak = m.group(1).lower() == "true"
    # Signed delay = disclosure day - event day.
    delay = disclosure_day - event_day
    # Late only when delay strictly exceeds the allowance; equality is timely.
    late = delay > allowance
    # Leak precedence is absolute (late_condition is still reported on its own merits).
    if leak:
        final = "immediate_escalation"
    elif late:
        final = "late_disclosure"
    else:
        final = "timely_disclosure"
    return {
        "final": final,
        "slots": {"disclosure_delay_days": delay, "late_condition": _bool(late)},
    }
