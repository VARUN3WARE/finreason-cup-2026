"""h052: required waste-cost reduction rate to hit a combined savings target.

energy savings  = energy expenditure * energy-reduction ratio      (checkpoint, USD)
waste savings   = target - energy savings
waste rate (%)  = waste savings / waste expenditure * 100            (final, percent)
"""

import re
from fractions import Fraction

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h052"


def _ratio(text: str) -> Fraction:
    """Energy-reduction ratio; accepts a plain ratio or a value stated in percent."""
    m = re.search(
        rf"energy[- ]reduction (?:ratio|rate)(?: of)? ({NUMBER})\s*(%|percent)?", text, flags=re.S
    )
    if m is None:
        raise ValueError("energy-reduction ratio not found")
    v = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        v /= 100
    return v


def solve(text: str, q: dict) -> dict:
    energy = grab(r"annual energy expenditure(?: of)? (?:USD )?\$?{N}", text)
    ratio = _ratio(text)
    waste = grab(r"waste-management expenditure (?:is |of )?(?:USD )?\$?{N}", text)
    target = grab(r"savings target(?: of)? (?:USD )?\$?{N}", text)

    energy_savings = energy * ratio
    waste_savings = target - energy_savings
    rate_pct = waste_savings / waste * 100

    return {
        "final": rate_pct,
        "slots": {"energy_savings_checkpoint": energy_savings},
    }
