"""Cluster h073 -- binding quoted purchase price for a target simple total return.

Structure (per-share USD):
    gross terminal sale proceeds G, holding-period dividend cash D,
    exit cost X (on selling), entry cost E (on buying, added to the quote P).
    Complete acquisition outlay      O = P + E
    Net terminal receipts            R = G + D - X
    Simple nonannualized total return = (R - O) / O  = target T  (a ratio)
    =>  R = (1 + T) * (P + E)  =>  P = R / (1 + T) - E

Ambiguities hunted and resolved
-------------------------------
A1. Are dividends part of "net terminal receipts"?  YES.
    - The return is a *total* return, and its definition has only two terms
      (net terminal receipts, outlay); if dividends were outside "receipts"
      they would be outside the return altogether, contradicting "total".
    - "Ignore ... discounting, and dividend reinvestment" => the dividend is
      plain cash added at face value with no timing adjustment.
    - The dividends carry 3 decimals (e.g. 20.445 -> receipts 100.445), which
      is exactly the half-up-at-the-cent trap the checkpoint spec tests; with
      dividends excluded the checkpoint would be an integer and the rounding
      instruction pointless.
    Note: the FINAL answer is the same under either reading (dividends end up
    in the numerator anyway); only the checkpoint depends on this.
A2. Target "ratio 0.25, where 0.20 means 20%"  => T is a plain ratio, used as
    is (no division by 100).
A3. Denominator of the return is the complete outlay P + E ("divided by that
    outlay"), not the bare quote.
A4. "Exit cost" is subtracted from the gross sale proceeds (slot text:
    "terminal receipts after exit cost"); "entry cost" is added to the quote.
A5. "Binding" price = the equality solution of return == target.  The text
    explicitly says the reported amount is the half-up rounded exact
    threshold, "not necessarily the greatest executable whole-cent quote",
    so NO floor to a whole cent and no inequality search.
A6. "Carry the threshold exactly": the unrounded receipts R feed the final
    formula; the checkpoint rounding (half-up to cents) is left to the
    framework, nothing displayed is fed back into the computation.
A7. No floor at zero / sign rule is stated, so a negative P would be returned
    as computed (does not arise in the three instances).
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h073"

# optional filler between the anchor words and the number ("of", "USD", "$")
_FILL = r"(?:\s+of)?(?:\s+USD)?\s*\$?\s*"


def _num(anchor: str, text: str) -> Fraction:
    return grab(anchor + _FILL + "{N}", text)


def _num_or_zero(anchor: str, text: str) -> Fraction:
    try:
        return _num(anchor, text)
    except ValueError:
        return Fraction(0)


def solve(text: str, q: dict) -> dict:
    G = _num(r"gross terminal sale proceeds", text)          # gross sale proceeds
    D = _num_or_zero(r"holding-period dividend cash", text)  # dividend cash
    X = _num(r"exit cost", text)                             # selling cost
    E = _num(r"entry cost", text)                            # buying cost
    T = _num(r"target ratio", text)                          # plain ratio (A2)

    # Net terminal receipts after exit cost, dividends included (A1, A4).
    R = G + D - X

    # (R - (P + E)) / (P + E) = T  =>  P = R / (1 + T) - E   (A3, A5)
    P = R / (1 + T) - E

    return {
        "final": P,
        "slots": {"net_receipts_checkpoint": R},
    }
