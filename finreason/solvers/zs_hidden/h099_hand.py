"""h099: back out the pre-shock crypto price from current price, loss ratio and a
rebound ratio expressed as a multiple of the loss ratio.

current = pre * (1 - loss) * (1 + rebound),   rebound = multiple * loss
pre     = current / ((1 - loss) * (1 + rebound))
"""
from fractions import Fraction
import re

from finreason.nums import grab, NUMBER, F

TEMPLATE_ID = "h099"


def _ratio(pattern: str, text: str) -> Fraction:
    """Number captured by pattern; converted from percent if followed by 'percent' / '%'."""
    rx = pattern.replace("{N}", f"({NUMBER})") + r"\s*(percent|%)?"
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    v = F(m.group(1))
    if m.group(2):
        v = v / 100
    return v


def solve(text: str, q: dict) -> dict:
    current = grab(r"currently priced at (?:USD\s*)?{N}", text)
    loss = _ratio(r"by (?:a )?loss ratio (?:of |equal to )?{N}", text)
    multiple = grab(r"rebound ratio equal to {N} times the (?:shock )?loss ratio", text)

    rebound = multiple * loss                      # checkpoint 1 (ratio)
    post_shock_factor = 1 - loss
    rebound_factor = 1 + rebound
    pre = current / (post_shock_factor * rebound_factor)

    return {"final": pre, "slots": {"rebound_ratio_checkpoint": rebound}}
