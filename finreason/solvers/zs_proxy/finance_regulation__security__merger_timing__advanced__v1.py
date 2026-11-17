from fractions import Fraction
import re
from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.security.merger_timing.advanced.v1"


def _flag(name: str, text: str) -> bool:
    m = re.search(name + r"\s+is\s+(true|false)", text, re.I)
    if m is None:
        raise ValueError(f"flag {name!r} not found")
    return m.group(1).lower() == "true"


def solve(text: str, q: dict) -> dict:
    event = grab(r"Event day offset is {N}", text)
    disc = grab(r"Disclosure day offset is {N}", text)
    allow = grab(r"Allowed delay in whole days is {N}", text)
    leak = _flag(r"Leak flag", text)
    delay = disc - event
    late = delay > allow  # strictly greater; equality is timely
    if leak:
        final = "immediate_escalation"
    elif late:
        final = "late_disclosure"
    else:
        final = "timely_disclosure"
    return {
        "final": final,
        "slots": {"disclosure_delay_days": delay, "late_condition": "true" if late else "false"},
    }
