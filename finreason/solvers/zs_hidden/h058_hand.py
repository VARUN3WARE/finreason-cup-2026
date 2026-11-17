"""h058 -- two-stage (primary + backup-on-misses) detection: required conditional backup ratio.

Structure (from the text):
  primary review detects ratio p of the population;
  backup review is applied only to the missed set (share 1 - p) and detects a conditional
  ratio b of that missed set, so the stages do not overlap;
  unique combined detection = p + (1 - p) * b.
  Required backup ratio so combined detection reaches target T:
      b = (T - p) / (1 - p), reported in percent (b * 100).

Checkpoint primary_miss_checkpoint = complement ratio remaining after primary review = 1 - p (ratio).

No floor at zero is stated in the text, so the literal formula value is returned (it is 0 when
p == T and negative when the stated "primary strictly below target" premise is broken, p > T).
"""

from fractions import Fraction
import re

from finreason.nums import NUMBER, F

TEMPLATE_ID = "h058"


def _ratio_after(pattern: str, text: str) -> Fraction:
    """Number captured by ``{N}``; a trailing 'percent' converts it to a ratio."""
    rx = pattern.replace("{N}", f"({NUMBER})") + r"(\s*(?:percent|%))?"
    m = re.search(rx, text, flags=re.S | re.I)
    if m is None:
        raise ValueError(f"pattern not found: {pattern!r}")
    v = F(m.group(1))
    if m.group(2):
        v /= 100
    return v


def solve(text: str, q: dict) -> dict:
    p = _ratio_after(
        r"primary review detects\s+(?:an?\s+)?(?:exact\s+)?(?:decimal\s+)?(?:ratio\s+)?(?:of\s+)?{N}",
        text,
    )
    t = _ratio_after(
        r"target\s+(?:unique\s+)?(?:combined\s+)?detection\s+ratio\s+(?:is|of)\s+{N}",
        text,
    )

    miss = 1 - p  # complement ratio remaining after primary review
    if miss == 0:
        required = Fraction(0)
    else:
        # p + miss * b = t  ->  b = (t - p) / miss
        required = (t - p) / miss

    return {
        "final": required * 100,  # percent
        "slots": {"primary_miss_checkpoint": miss},
    }
