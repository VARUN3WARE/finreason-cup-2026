"""h070: reverse a transfer fee chain (proportional fee -> fixed fee -> rebate credit).

Forward chain: net = G * (1 - f) - fixed + rebate.
Reverse (as instructed): remove the rebate, restore the fixed fee, divide by the
proportional-fee retention ratio (1 - f).
Checkpoint pre_rebate_checkpoint = receipt required before the rebate is applied
= target - rebate.
"""

import re
from fractions import Fraction

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h070"


def _fee_ratio(text: str) -> Fraction:
    m = re.search(r"proportional fee (?:ratio|rate)? ?of (" + NUMBER + r")\s*(percent|%)?", text)
    if m is None:
        raise ValueError("fee ratio not found")
    v = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        v /= 100
    return v


def solve(text: str, q: dict) -> dict:
    f = _fee_ratio(text)
    fixed = grab(r"fixed (?:network )?fee of {N}", text)
    rebate = grab(r"rebate of {N}", text)
    target = grab(r"to obtain exactly {N}", text)

    pre_rebate = target - rebate          # receipt needed before the rebate is credited
    pre_fixed = pre_rebate + fixed        # amount after proportional fee, before fixed fee
    gross = pre_fixed / (1 - f)           # divide by retention ratio

    return {"final": gross, "slots": {"pre_rebate_checkpoint": pre_rebate}}
