"""Beneficial ownership: total = direct + indirect; threshold met when total >= threshold;
enhanced review (final) = threshold met OR control flag."""

import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "fp.finance_regulation.aml.beneficial_ownership.intermediate.v1"


def _flag(pattern: str, text: str) -> bool:
    m = re.search(pattern + r"\s+(true|false)\b", text, flags=re.I | re.S)
    if m is None:
        raise ValueError(f"flag not found: {pattern!r}")
    return m.group(1).lower() == "true"


def _meets(value: Fraction, threshold: Fraction, text: str) -> bool:
    # Stated rule: "at least the threshold" (non-strict). Fall back to strict only if the text says so.
    if re.search(r"total ownership is (strictly )?(above|greater than|exceeds|more than) the threshold", text):
        return value > threshold
    return value >= threshold


def _tok(b: bool) -> str:
    return "true" if b else "false"


def solve(text: str, q: dict) -> dict:
    direct = grab(r"Direct ownership percent is {N}", text)
    indirect = grab(r"Indirect ownership percent is {N}", text)
    control = _flag(r"control flag is", text)
    threshold = grab(r"ownership threshold percent is {N}", text)
    total = direct + indirect
    met = _meets(total, threshold, text)
    final = met or control
    return {
        "final": _tok(final),
        "slots": {"total_ownership_percent": total, "ownership_threshold_met": _tok(met)},
    }
