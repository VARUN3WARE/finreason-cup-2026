"""Composite compliance risk: residual = inherent * (1 - control effectiveness); composite = residual + incident."""
import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.compliance.composite_risk.advanced.v1"


def _flag(pattern: str, text: str) -> bool:
    m = re.search(pattern, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"flag not found: {pattern!r}")
    return m.group(1).lower() in ("true", "yes", "on", "set", "active")


def solve(text: str, q: dict) -> dict:
    inherent = grab(r"Inherent risk score is {N}", text)
    control = grab(r"Control effectiveness ratio is {N}", text)
    incident = grab(r"Incident score is {N}", text)
    override = _flag(r"High-risk override is (\w+)", text)
    high_thr = grab(r"composite risk is at least {N} or override", text)
    med_thr = grab(r"medium_risk when composite is at least {N}", text)

    residual = inherent * (1 - control)
    composite = residual + incident

    high = composite >= high_thr or override
    if high:
        final = "high_risk"
    elif composite >= med_thr:
        final = "medium_risk"
    else:
        final = "low_risk"
    return {
        "final": final,
        "slots": {
            "residual_risk_score": residual,
            "composite_risk_score": composite,
            "high_trigger": "true" if high else "false",
        },
    }
