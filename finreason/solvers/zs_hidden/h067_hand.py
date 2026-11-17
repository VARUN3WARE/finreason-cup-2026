"""h067: premium threshold at which a cash-settled option's simple expiration ROI hits a target.

ROI = (intrinsic - fee - premium) / premium = target
  => premium = (intrinsic - fee) / (1 + target)
"""

import re
from fractions import Fraction

from finreason.nums import grab

TEMPLATE_ID = "h067"


def _first(patterns, text):
    for p in patterns:
        try:
            return grab(p, text)
        except ValueError:
            continue
    raise ValueError(f"none of the patterns matched: {patterns!r}")


def solve(text: str, q: dict) -> dict:
    s = _first([r"terminal stock price (?:of )?(?:USD )?{N}",
                r"terminal (?:share |underlying )?price (?:of )?(?:USD )?{N}"], text)
    k = _first([r"strike price (?:of )?(?:USD )?{N}", r"strike (?:of )?(?:USD )?{N}"], text)
    fee = _first([r"settlement fee (?:of )?(?:USD )?{N}", r"fee (?:of )?(?:USD )?{N}"], text)

    # Target: stated as a ratio ("target ratio 0.25, where 0.20 means 20%") or, defensively, in percent.
    m_pct = re.search(r"target (?:ROI )?(?:of )?(-?\d+(?:\.\d+)?) ?(?:percent|%)", text)
    if m_pct and not re.search(r"target ratio", text):
        target = Fraction(m_pct.group(1)) / 100
    else:
        target = _first([r"target ratio (?:of )?{N}", r"target (?:ROI )?(?:of )?{N}"], text)

    is_put = re.search(r"\bput\b", text, flags=re.I) is not None and \
        re.search(r"\bcall\b", text, flags=re.I) is None
    if is_put:
        intrinsic = max(k - s, Fraction(0))
    else:
        intrinsic = max(s - k, Fraction(0))

    # (intrinsic - fee - P) / P = target  =>  P = (intrinsic - fee) / (1 + target)
    premium = (intrinsic - fee) / (1 + target)

    return {"final": premium, "slots": {"intrinsic_checkpoint": intrinsic}}
