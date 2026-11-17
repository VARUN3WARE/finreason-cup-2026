"""h008: straight-line depreciation -- back out the residual value that yields a
target carrying amount after a given fraction of the depreciable life.

carrying = cost - f * (cost - residual)
accumulated depreciation = cost - carrying
residual = cost - accumulated / f
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, grab

TEMPLATE_ID = "h008"


def _elapsed_fraction(text: str) -> Fraction:
    m = re.search(
        rf"({NUMBER})\s*(percent|%)?\s*(?:of\s+(?:its|the)\s+(?:\w+\s+)?(?:depreciable|useful)\s+life)",
        text,
        flags=re.S | re.I,
    )
    if m is None:
        raise ValueError("elapsed fraction not found")
    v = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        v /= 100
    return v


def solve(text: str, q: dict) -> dict:
    cost = grab(r"original cost (?:of )?(?:USD )?{N}", text)
    f = _elapsed_fraction(text)
    target = grab(r"target carrying amount (?:of )?(?:USD )?{N}", text)

    accumulated = cost - target
    residual = cost - accumulated / f

    return {
        "final": residual,
        "slots": {"implied_depreciation_checkpoint": accumulated},
    }
