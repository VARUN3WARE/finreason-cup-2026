"""h057: unit gross-profit retention after a price discount and a unit-cost change.

baseline unit GP   = P0 * m0               (margin ratio on the undiscounted price)
discounted price   = P0 * (1 - d)          (d = discount as a fraction of the original price)
post-change GP     = discounted price - post-change unit cost
retention (pct)    = post-change GP / baseline GP * 100
"""
from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import grab, F, NUMBER

TEMPLATE_ID = "h057"


def _first(patterns, text):
    for p in patterns:
        try:
            return grab(p, text)
        except ValueError:
            continue
    raise ValueError(f"none of the patterns matched: {patterns!r}")


def _margin_ratio(text: str) -> Fraction:
    rx = re.compile(r"baseline gross margin (ratio|percentage|percent|rate)?\s*(?:is|of)\s*(" + NUMBER + r")\s*(percent|%)?", re.I)
    m = rx.search(text)
    if m is None:
        raise ValueError("baseline gross margin not found")
    v = F(m.group(2))
    if m.group(3) or (m.group(1) and m.group(1).lower() in ("percentage", "percent")):
        v = v / 100
    return v


def _discounted_price(text: str, p0: Fraction) -> Fraction:
    # "discounted by 0.2 of the original price"
    m = re.search(r"discounted by (" + NUMBER + r")\s*(percent|%)?\s*(USD)?\s*(of the original price)?", text, re.I)
    if m is None:
        # "discounted to X USD"
        return grab(r"discounted to (?:USD )?{N}", text)
    v = F(m.group(1))
    if m.group(2):
        return p0 * (1 - v / 100)
    if m.group(3) and not m.group(4):
        return p0 - v  # absolute USD discount
    return p0 * (1 - v)


def solve(text: str, q: dict) -> dict:
    p0 = _first([r"original unit price is (?:USD )?{N}", r"original (?:selling )?price (?:per unit )?is (?:USD )?{N}"], text)
    m0 = _margin_ratio(text)
    c1 = _first([r"post-change unit cost is (?:USD )?{N}", r"unit cost (?:becomes|changes to|is) (?:USD )?{N}"], text)

    base_gp = p0 * m0
    p1 = _discounted_price(text, p0)
    new_gp = p1 - c1
    retention = new_gp / base_gp * 100

    return {"final": retention, "slots": {"discounted_unit_price_checkpoint": p1}}
