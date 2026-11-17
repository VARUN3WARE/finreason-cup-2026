"""h048: revenue downturn then required recovery rate.

post = start * (1 - downturn_ratio)          (downturn ratio = fraction of revenue lost)
rate = (target - post) / post, reported in percent.
"""
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h048"


def _first(patterns, text):
    last = None
    for p in patterns:
        try:
            return grab(p, text)
        except ValueError as e:  # try the next anchor
            last = e
    raise last


def solve(text: str, q: dict) -> dict:
    start = _first([
        r"starts with revenue (?:of )?(?:USD )?\$?{N}",
        r"revenue (?:of )?(?:USD )?\$?{N}",
    ], text)
    d = _first([
        r"downturn ratio (?:of )?{N}",
        r"downturn (?:of )?{N}",
    ], text)
    if "downturn ratio" not in text and "percent" in text.split("downturn", 1)[-1][:40]:
        d = d / 100
    target = _first([
        r"target revenue (?:of )?(?:USD )?\$?{N}",
        r"target (?:of )?(?:USD )?\$?{N}",
    ], text)

    post = Fraction(start) * (1 - d)
    needed = target - post
    rate = needed / post
    return {"final": rate * 100, "slots": {"post_downturn_checkpoint": post}}
