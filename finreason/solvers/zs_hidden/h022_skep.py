"""h022 -- post-earnout percentage ownership of the acquirer's common-share base.

Structure (identical across the 3 instances, numbers differ):
  * Acquirer predeal common shares: aggregate reference equity value E at one
    fixed contractual share price P.
  * Upfront base consideration B (excludes the earnout); fraction c of B is paid
    in cash, the remainder (1 - c) * B in acquirer common shares at price P.
  * Earnout settlement value S, incremental to B, settled entirely in common
    shares at the same unchanged price P.
  * No other issuance / repurchase / disposal / option / conversion / price change.
  * Sellers retain all upfront shares through the measurement date.

AMBIGUITY HUNT -- resolutions with textual evidence:
  A1  Share counts vs. values.  P is never given, but every share-settled amount
      is converted at "one fixed contractual share price" / "the same unchanged
      price", so predeal shares = E/P, upfront shares = (1-c)B/P, earnout shares
      = S/P.  P cancels in the ownership ratio, so the answer is a pure value
      ratio.  No whole-share rounding is possible (P unknown) and none is stated.
  A2  "0.2 of that base is paid in cash": a plain fraction of B, not a percent
      ("of that base", no "percent").  The solver still divides by 100 if an
      instance ever phrases it as "{N} percent of that base".
  A3  Cash portion: creates no shares, so it is excluded from both the sellers'
      holding and the share base.  Only "the remainder in acquirer common shares"
      becomes seller shares.
  A4  Earnout: "incremental to the base consideration" -> added on top of B, not
      carved out of it; "settled entirely in common shares" -> all of S becomes
      seller shares (no cash split applied to the earnout).  "Fully realized" ->
      the full settlement value S is paid.
  A5  Denominator: "post-settlement ... common-share base" at the "post-earnout
      measurement date" -> includes predeal shares + upfront stock + earnout
      stock.  "Assume no other issuance..." -> nothing else is in the base.
  A6  Numerator: sellers hold upfront stock + earnout stock ("retain all upfront
      shares through the measurement date" -> no disposal).
  A7  Units: final is `percent` -> ratio * 100, returned unrounded (framework
      rounds half-up to 2 dp).  Checkpoint is `usd_million` -> the text's values
      are already in the problem's money unit, so (1-c)*B is returned as-is.
  A8  Checkpoint = "upfront consideration settled in acquirer common shares" =
      (1-c) * B only.  It excludes the earnout (earnout is not "upfront") and
      excludes the cash portion.

Result:
  upfront_stock = (1 - c) * B
  seller_value  = upfront_stock + S
  total_value   = E + upfront_stock + S
  final (percent) = 100 * seller_value / total_value
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h022"


def _cash_fraction(text: str) -> Fraction:
    """Fraction of the base paid in cash; accepts '0.2 of that base' or
    '20 percent of that base' / '20% of that base'."""
    m = re.search(
        rf"({NUMBER})\s*(percent|%)?\s+of\s+(?:that|the)\s+base(?:\s+consideration)?\s+is\s+paid\s+in\s+cash",
        text,
        flags=re.S,
    )
    if m is None:
        # Fallback: first number followed by "of that base".
        m = re.search(rf"({NUMBER})\s*(percent|%)?\s+of\s+(?:that|the)\s+base", text, flags=re.S)
    if m is None:
        raise ValueError("cash fraction not found")
    val = F(m.group(1))
    if m.group(2):
        val = val / 100
    return val


def solve(text: str, q: dict) -> dict:
    # E: aggregate reference equity value of the acquirer's PREDEAL common shares.
    predeal_value = grab(r"aggregate reference equity value\s+(?:of\s+)?(?:USD\s+)?{N}", text)

    # B: upfront base consideration (excludes the earnout).
    base = grab(r"[Uu]pfront base consideration (?:is|of)\s+(?:USD\s+)?{N}", text)

    # c: fraction of B paid in cash; remainder in acquirer common shares.
    cash_frac = _cash_fraction(text)

    # S: earnout settlement value, incremental to B, settled entirely in shares.
    earnout = grab(r"earnout[^.]*?settlement value\s+(?:of\s+)?(?:USD\s+)?{N}", text)

    # Upfront consideration settled in acquirer common shares (checkpoint).
    upfront_stock = (Fraction(1) - cash_frac) * base

    # Sellers' holding and the post-settlement common-share base (both in value
    # at the single fixed price P; P cancels in the ratio).
    seller_value = upfront_stock + earnout
    total_value = predeal_value + upfront_stock + earnout

    ownership_pct = Fraction(100) * seller_value / total_value

    return {
        "final": ownership_pct,
        "slots": {
            "upfront_stock_consideration_checkpoint": upfront_stock,
        },
    }
