"""h018: multi-stage common-share issuance, pro forma EPS floor, choose option A / B / neither.

Pro forma EPS of an option = (current EPS + added earnings per current share)
                             / (1 + per-stage share-base increase) ** stages.
An option qualifies iff its exact pro forma EPS >= the floor ("at least").
Pick the qualifying option with the higher exact EPS; exact tie -> option_a;
none qualifying -> neither_option.
Checkpoint: Option A share-base multiple after one stage = 1 + per-stage increase.
"""

import re
from fractions import Fraction

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h018"

_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
          "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def _stages(text: str) -> list[int]:
    """Exponents of the cumulative multiples for A and B (fallback: stated stage count)."""
    exps = [int(m) for m in re.findall(r"\(1 \+ the ratio\)\^(\d+)", text)]
    if len(exps) >= 2:
        return exps[:2]
    m = re.search(r"exactly (\w+) sequential", text)
    n = _WORDS.get(m.group(1).lower()) if m else None
    if n is None and m is not None and m.group(1).isdigit():
        n = int(m.group(1))
    if exps and n is None:
        n = exps[0]
    return [n, n]


def solve(text: str, q: dict) -> dict:
    eps0 = grab(r"current common EPS {N}", text)
    floor = grab(r"pro forma EPS of at least {N}", text)
    add_a = grab(r"Option A adds total earnings of {N} per current share", text)
    r_a = grab(r"Option A.*?per-stage share-base increase is {N}", text)
    add_b = grab(r"Option B analogously adds {N} per current share", text)
    r_b = grab(r"Option B.*?per-stage increase {N}", text)
    n_a, n_b = _stages(text)

    mult_a = (1 + r_a) ** n_a
    mult_b = (1 + r_b) ** n_b
    eps_a = (eps0 + add_a) / mult_a
    eps_b = (eps0 + add_b) / mult_b

    qa = eps_a >= floor
    qb = eps_b >= floor
    if qa and qb:
        final = "option_a" if eps_a >= eps_b else "option_b"
    elif qa:
        final = "option_a"
    elif qb:
        final = "option_b"
    else:
        final = "neither_option"

    return {"final": final,
            "slots": {"a_one_stage_share_multiple_checkpoint": Fraction(1) + r_a}}
