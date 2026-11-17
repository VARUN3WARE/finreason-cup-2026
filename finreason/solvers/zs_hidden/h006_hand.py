"""h006: partial factor exposure -> required signed factor shock (in percent).

Model (linear factor exposure):
    exposed value      E = portfolio value * exposed share
    value change      dV = E * sensitivity * shock
    required shock     s = target change / (E * sensitivity)   -> reported * 100 (percent)
"""

from fractions import Fraction
import re

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h006"


def _share(text: str) -> Fraction:
    # "only share 0.5 is exposed" (fraction); tolerate "share 50 percent"/"50%" forms.
    m = re.search(rf"share\s+(?:of\s+)?({NUMBER})\s*(percent|%)?", text)
    if m is None:
        raise ValueError("exposed share not found")
    v = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        v /= 100
    return v


def solve(text: str, q: dict) -> dict:
    value = grab(r"worth (?:USD )?\$?{N}", text)
    share = _share(text)
    beta = grab(r"sensitivity (?:of )?{N}", text)
    target = grab(r"value change (?:of )?(?:USD )?\$?{N}", text)

    exposed = value * share
    shock = target / (exposed * beta)          # signed shock as a ratio
    return {
        "final": shock * 100,                  # percent
        "slots": {"exposed_value_checkpoint": exposed},
    }
