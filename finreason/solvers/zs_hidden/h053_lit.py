"""h053 -- literal transcription: percentage-scaled HHI-style concentration of
three modeled exposure categories (P_i = volume * assessment ratio)."""

import re
from fractions import Fraction

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h053"


def _category(text: str, k: int):
    # "Category k has [covered volume] [USD] V [USD] and [decimal assessment ratio] R"
    rx = (
        rf"Category\s+{k}\s+has\s+(?:covered\s+volume\s+)?(?:USD\s+)?({NUMBER})\s*(?:USD\s+)?"
        rf"and\s+(?:(?:a\s+)?decimal\s+assessment\s+ratio\s+(?:of\s+)?)?({NUMBER})\s*(percent|%)?"
    )
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"category {k} not found")
    volume = F(m.group(1))
    ratio = F(m.group(2))
    if m.group(3):  # stated as a percent rather than a decimal ratio
        ratio = ratio / 100
    return volume, ratio


def solve(text: str, q: dict) -> dict:
    # "Category 1 has covered volume ... USD and decimal assessment ratio ...; Category 2 has ...; Category 3 has ..."
    volumes, ratios = [], []
    for k in (1, 2, 3):
        v, r = _category(text, k)
        volumes.append(v)
        ratios.append(r)

    # "define modeled exposure P_i as volume times assessment ratio"
    P = [volumes[i] * ratios[i] for i in range(3)]

    # "define s_i as P_i divided by the total of the three exposures"
    total = sum(P, Fraction(0))
    s = [p / total for p in P]

    # "define H as the sum of the three squared shares"
    H = sum((si ** 2 for si in s), Fraction(0))

    # "Report 100H as a percentage."
    final = 100 * H

    return {
        "final": final,
        "slots": {
            "category_1_exposure_checkpoint": P[0],
            "category_2_exposure_checkpoint": P[1],
        },
    }
