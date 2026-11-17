"""h052 -- literal transcription solver.

Sentence by sentence:
  1. "annual energy expenditure E and an achieved energy-reduction ratio r"
  2. "Annual waste-management expenditure is W."
  3. "To reach the combined annual savings target T, compute the waste-cost
     reduction rate that must be reported, expressed as a percentage."

  energy savings      = E * r                      (checkpoint, USD)
  required waste save = T - energy savings
  waste rate          = required waste save / W    -> * 100 (percent)
"""

import re
from fractions import Fraction

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h052"


def _ratio(pattern: str, text: str) -> Fraction:
    """Number after the phrase; divided by 100 if stated as a percent."""
    rx = pattern.replace("{N}", f"({NUMBER})") + r"\s*(%|percent)?"
    m = re.search(rx, text, flags=re.S)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    v = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        v /= 100
    return v


def solve(text: str, q: dict) -> dict:
    # Sentence 1: energy expenditure and achieved energy-reduction ratio
    energy_expenditure = grab(r"energy expenditure (?:of )?(?:USD |\$)?{N}", text)
    energy_reduction_ratio = _ratio(r"energy-reduction ratio (?:of )?{N}", text)

    # Sentence 2: waste-management expenditure
    waste_expenditure = grab(r"waste-management expenditure (?:is |of )?(?:USD |\$)?{N}", text)

    # Sentence 3: combined savings target
    savings_target = grab(r"savings target (?:of )?(?:USD |\$)?{N}", text)

    # Savings contributed by energy reduction
    energy_savings = energy_expenditure * energy_reduction_ratio

    # Savings that the waste-cost reduction must deliver to reach the target
    required_waste_savings = savings_target - energy_savings

    # Waste-cost reduction rate, expressed as a percentage
    waste_rate = required_waste_savings / waste_expenditure
    waste_rate_pct = waste_rate * 100

    return {
        "final": waste_rate_pct,
        "slots": {"energy_savings_checkpoint": energy_savings},
    }
