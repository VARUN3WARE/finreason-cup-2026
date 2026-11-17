"""h003: shared cost pool allocation that equalises two segments' after-tax profit margins.

Segment s: revenue R_s, pre-shared-cost pre-tax margin m_s, tax rate t_s.
Pre-shared-cost pre-tax profit P_s = R_s * m_s.  Pool C; A gets x*C, B gets (1-x)*C.
After-tax profit = pre-tax profit minus tax on the positive pre-tax profit.
Solve (afterTax_A / R_A) == (afterTax_B / R_B) for x; report x in percent.
Checkpoints: C / R_A and C / R_B (ratios).
"""

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h003"


def _rate(text: str, label: str, word: str) -> Fraction:
    rx = rf"Segment {label} has(?:(?!Segment ).)*?{word}\s+({NUMBER})\s*(percent|%)?"
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"cannot find {word} for segment {label}")
    v = F(m.group(1))
    if m.group(2):
        v = v / 100
    return v


def _segment(text: str, label: str):
    m = re.search(rf"Segment {label} has revenue\s+({NUMBER})", text)
    if m is None:
        raise ValueError(f"cannot find revenue for segment {label}")
    rev = F(m.group(1))
    margin = _rate(text, label, r"profit margin")
    tax = _rate(text, label, r"tax rate")
    return rev, margin, tax


def solve(text: str, q: dict) -> dict:
    ra, ma, ta = _segment(text, "A")
    rb, mb, tb = _segment(text, "B")
    m = re.search(rf"shared deductible cost pool of\s+({NUMBER})", text)
    if m is None:
        m = re.search(rf"cost pool of\s+({NUMBER})", text)
    c = F(m.group(1))

    pa = ra * ma  # pre-shared-cost pre-tax profit of A
    pb = rb * mb

    def after_tax(p, t):
        return p - t * p if p > 0 else p

    # Margin_A(x) = kA * (pa - c x) / ra, Margin_B(x) = kB * (pb - c + c x) / rb,
    # where k = (1 - t) if the resulting pre-tax profit is positive, else 1.
    x = None
    for apply_a in (True, False):
        for apply_b in (True, False):
            ka = (1 - ta) if apply_a else Fraction(1)
            kb = (1 - tb) if apply_b else Fraction(1)
            denom = c * (ka * rb + kb * ra)
            if denom == 0:
                continue
            cand = (ka * pa * rb - kb * (pb - c) * ra) / denom
            prof_a = pa - cand * c
            prof_b = pb - (1 - cand) * c
            if (prof_a > 0) == apply_a and (prof_b > 0) == apply_b:
                if after_tax(prof_a, ta) / ra == after_tax(prof_b, tb) / rb:
                    x = cand
                    break
        if x is not None:
            break
    if x is None:
        raise ValueError("no consistent allocation found")

    return {
        "final": x * 100,
        "slots": {
            "segment_a_shared_cost_burden_ratio_checkpoint": c / ra,
            "segment_b_shared_cost_burden_ratio_checkpoint": c / rb,
        },
    }
