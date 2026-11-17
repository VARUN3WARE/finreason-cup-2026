"""Composite compliance risk: residual = inherent * (1 - control effectiveness);
composite = residual + incident; tiered classification with high-risk override precedence."""

import re
from fractions import Fraction

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "fp.finance_regulation.compliance.composite_risk.advanced.v1"

_CMP = r"(at least|greater than or equal to|no less than|not less than|above|greater than|more than|exceeds|over|at or above)"


def _test(op: str, value: Fraction, thr: Fraction) -> bool:
    op = op.lower()
    if op in ("above", "greater than", "more than", "exceeds", "over"):
        return value > thr
    return value >= thr


def _rule(label: str, text: str, default_thr: Fraction):
    m = re.search(label + r" when composite(?: risk)?(?: score)? is " + _CMP + r" (" + NUMBER + r")", text)
    if m is None:
        m = re.search(label + r" when composite(?: risk)?(?: score)? " + _CMP + r" (" + NUMBER + r")", text)
    if m is None:
        return "at least", default_thr
    return m.group(1), Fraction(m.group(2).replace(",", ""))


def solve(text: str, q: dict) -> dict:
    inherent = grab(r"Inherent risk score is {N}", text)
    control = grab(r"Control effectiveness ratio is {N}", text)
    incident = grab(r"Incident score is {N}", text)
    m = re.search(r"High-risk override is (true|false)", text, flags=re.I)
    override = bool(m) and m.group(1).lower() == "true"

    residual = inherent * (1 - control)
    composite = residual + incident

    hi_op, hi_thr = _rule("high_risk", text, Fraction(8))
    md_op, md_thr = _rule("medium_risk", text, Fraction(5))

    high = _test(hi_op, composite, hi_thr) or override
    if high:
        final = "high_risk"
    elif _test(md_op, composite, md_thr):
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
