from fractions import Fraction
import re

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h038"


def _rate(pattern: str, text: str) -> Fraction:
    """Parse a rate; if followed by 'percent' or '%', convert to a ratio."""
    rx = pattern.replace("{N}", f"({NUMBER})") + r"\s*(percent|%)?"
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    v = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        v /= 100
    return v


def solve(text: str, q: dict) -> dict:
    loss = grab(r"eligible loss magnitude of {N}", text)
    tax_rate = _rate(r"current-year tax rate is {N}", text)
    principal = grab(r"original {N} USD principal", text)
    intended = _rate(r"intended rate {N}", text)
    shortfall = _rate(r"tracking shortfall {N}", text)
    years = int(grab(r"compound annually for {N} years", text))

    tax_reduction = loss * tax_rate
    replacement_rate = intended - shortfall

    harvest_tw = (principal + tax_reduction) * (1 + replacement_rate) ** years
    no_harvest_tw = principal * (1 + intended) ** years
    advantage = harvest_tw - no_harvest_tw

    return {
        "final": advantage,
        "slots": {"immediate_tax_reduction_checkpoint": tax_reduction},
    }
