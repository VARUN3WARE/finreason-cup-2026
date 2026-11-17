"""h053: percentage-scaled HHI-style concentration of three modeled exposures.

P_i = covered volume_i * decimal assessment ratio_i
s_i = P_i / (P_1 + P_2 + P_3)
final = 100 * sum(s_i^2)  (percent)
slots: P_1, P_2 (USD, before normalization).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import F, NUMBER

TEMPLATE_ID = "h053"


def _category(text: str, k: int) -> tuple[Fraction, Fraction]:
    # e.g. "Category 1 has covered volume 4096.004 USD and decimal assessment ratio 0.5;"
    #      "Category 2 has 11794.812 USD and 0.5;"
    rx = (
        rf"Category\s+{k}\s+has\s+(?:covered\s+volume\s+)?(?:USD\s+)?({NUMBER})\s*(?:USD)?"
        rf"\s+and\s+(?:a\s+)?(?:decimal\s+)?(?:assessment\s+ratio\s+(?:of\s+)?)?({NUMBER})(\s*(?:percent|%))?"
    )
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"category {k} not found")
    vol = F(m.group(1))
    ratio = F(m.group(2))
    if m.group(3):
        ratio /= 100
    return vol, ratio


def solve(text: str, q: dict) -> dict:
    exposures = []
    for k in (1, 2, 3):
        vol, ratio = _category(text, k)
        exposures.append(vol * ratio)
    total = sum(exposures, Fraction(0))
    h = sum(((p / total) ** 2 for p in exposures), Fraction(0))
    slots = {
        "category_1_exposure_checkpoint": exposures[0],
        "category_2_exposure_checkpoint": exposures[1],
    }
    return {"final": 100 * h, "slots": slots}
