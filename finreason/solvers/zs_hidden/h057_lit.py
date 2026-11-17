"""h057 -- unit gross-profit retention after a price discount and unit-cost change.

Literal transcription of the question:
  - original unit price P (USD)
  - baseline gross margin ratio m, computed on the same undiscounted price and per-unit basis
      => baseline unit gross profit = P * m
  - comparison scenario: selling price discounted by d of the original price
      => discounted unit price = P - d * P = P * (1 - d)          (checkpoint, USD)
    post-change unit cost C (USD)
      => post-change unit gross profit = discounted price - C
  - retention percentage = post-change unit GP / baseline unit GP * 100   (percent; not a margin)
"""

import re
from fractions import Fraction

from finreason.nums import grab, NUMBER

TEMPLATE_ID = "h057"


def _discount_fraction(text: str) -> Fraction:
    # "discounted by 0.2 of the original price" (fraction of the original price)
    m = re.search(rf"discounted by ({NUMBER})\s*(percent|%)?", text)
    if m is None:
        raise ValueError("discount not found")
    d = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        d = d / 100
    return d


def solve(text: str, q: dict) -> dict:
    # Sentence 1: original unit price.
    original_price = grab(r"original unit price is (?:USD )?{N}", text)

    # Sentence 2: baseline gross margin ratio on the same undiscounted unit price.
    m = re.search(rf"baseline gross margin ratio is ({NUMBER})\s*(percent|%)?", text)
    if m is None:
        raise ValueError("baseline margin not found")
    baseline_margin = Fraction(m.group(1).replace(",", ""))
    if m.group(2):
        baseline_margin = baseline_margin / 100
    baseline_unit_cost = original_price * (1 - baseline_margin)
    baseline_unit_gp = original_price - baseline_unit_cost  # = P * m

    # Sentence 3: discount of the original price and post-change unit cost.
    discount = _discount_fraction(text)
    discounted_price = original_price - discount * original_price
    post_change_unit_cost = grab(r"post-change unit cost is (?:USD )?{N}", text)
    post_change_unit_gp = discounted_price - post_change_unit_cost

    # Sentence 4-5: share of original per-unit gross profit retained, in percent.
    retention_pct = post_change_unit_gp / baseline_unit_gp * 100

    return {
        "final": retention_pct,
        "slots": {"discounted_unit_price_checkpoint": discounted_price},
    }
