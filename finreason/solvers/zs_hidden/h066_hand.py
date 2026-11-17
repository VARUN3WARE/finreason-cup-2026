"""h066: ESG project -- maximum initial investment meeting a required ROI.

net annual benefit = energy savings + water savings - maintenance cost
PV of net benefits = net annual benefit * full-horizon PV multiplier
ROI = (PV - I) / I  (strictly decreasing in I > 0)  =>  max I with ROI >= target is I = PV / (1 + ROI)
"""

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h066"

_CUR = r"(?:USD\s*|\$\s*)?"


def _ratio(text: str) -> Fraction:
    """Required ROI as a plain ratio (converts if stated in percent)."""
    m = re.search(r"required ROI(?: ratio)?(?: of)? (" + NUMBER + r")\s*(percent|%)?", text)
    if m is None:
        raise ValueError("required ROI not found")
    v = F(m.group(1))
    return v / 100 if m.group(2) else v


def solve(text: str, q: dict) -> dict:
    energy = grab(r"annual energy savings of " + _CUR + r"{N}", text)
    water = grab(r"annual water savings of " + _CUR + r"{N}", text)
    maint = grab(r"annual maintenance cost of " + _CUR + r"{N}", text)
    mult = grab(r"present-value multiplier for these recurring net benefits is {N}", text)
    roi = _ratio(text)

    net = energy + water - maint
    pv = net * mult
    inv = pv / (1 + roi)

    return {"final": inv, "slots": {"annual_net_benefit_checkpoint": net}}
