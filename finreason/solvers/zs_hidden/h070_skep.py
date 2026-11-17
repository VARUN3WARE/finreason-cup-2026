"""h070 -- reverse a three-stage transfer-fee chain to find the required gross amount.

Forward chain stated in the text (in this order):
    gross G
      -> charged a proportional fee (ratio r)            : G * (1 - r)
      -> then a fixed network fee f                       : G * (1 - r) - f
      -> after which a rebate b is credited               : G * (1 - r) - f + b  = net N (recipient receives)

Reverse chain (the text spells out the order explicitly):
    1. remove the rebate                   : P = N - b          <- checkpoint "pre_rebate_checkpoint"
    2. restore the fixed fee               : A = P + f
    3. divide by the retention ratio       : G = A / (1 - r)    <- final answer

AMBIGUITY HUNT (skeptic pass) and resolutions
----------------------------------------------
A1. "proportional fee ratio of 0.2" -- ratio or percent?
    The word is "ratio" and the value is 0.2, so it is a plain ratio (20%). The "retention ratio" is
    1 - r = 0.8. Defensive handling: if a variant says "percent"/"%", divide by 100.
A2. Fee base: is the proportional fee charged on the gross (G * r) or grossed-up from the net?
    The text says the transfer "is charged a proportional fee ratio", i.e. the fee is a fraction of the
    transfer (gross), and the reverse instruction says "dividing by the proportional-fee retention ratio",
    i.e. G = A / (1 - r).  Multiplying by (1 + r) would be a different (wrong) model.
A3. Order of the additive stages (fixed fee, rebate): stated as fee first then rebate; reverse order is
    rebate removed first, then fee restored. Because both are additive the final G is order-independent,
    but the checkpoint "receipt required before applying the rebate" is unambiguously N - b (the amount the
    recipient would have had with no rebate credit), NOT N - b + f.
A4. Sign of the rebate: "credited" -> it increases the recipient's receipt, so reversing it SUBTRACTS b.
A5. "Receipt required before applying the rebate" is in USD, same unit as the final; 2 dp half-up applied
    by the framework. We return the exact Fraction (no internal rounding anywhere -- the text says
    "carry all arithmetic exactly" and rounds only the reported value).
A6. No floor at zero, no thresholds, no tie rules in this template; sign preserved if b > N.
A7. "exactly 101 USD" is the NET amount the recipient obtains (post-rebate), which is the starting point of
    the reverse chain -- not the pre-rebate amount.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h070"


def _first(patterns: list[str], text: str) -> Fraction:
    for p in patterns:
        try:
            return grab(p, text)
        except ValueError:
            continue
    raise ValueError(f"none of the patterns matched: {patterns!r}")


def _proportional_fee_ratio(text: str) -> Fraction:
    """Proportional fee as a plain ratio (handles a 'percent' / '%' variant defensively)."""
    rx = (
        r"proportional[\s-]+fee\s+(?:ratio|rate|of)\s*(?:of\s*)?(?:USD\s*)?(" + NUMBER + r")"
        r"\s*(percent|%)?"
    )
    m = re.search(rx, text, flags=re.I | re.S)
    if m is None:
        # fallback: generic "fee ratio of X"
        rx2 = r"fee\s+ratio\s+of\s*(" + NUMBER + r")\s*(percent|%)?"
        m = re.search(rx2, text, flags=re.I | re.S)
    if m is None:
        raise ValueError("proportional fee ratio not found")
    r = F(m.group(1))
    if m.group(2):
        r = r / 100
    return r


def solve(text: str, q: dict) -> dict:
    r = _proportional_fee_ratio(text)                              # proportional fee ratio (A1)
    f = _first(
        [
            r"fixed[^.]*?fee\s+of\s+(?:USD\s*)?{N}",               # "fixed network fee of 4 USD"
            r"fixed\s+fee\s+of\s+(?:USD\s*)?{N}",
            r"network\s+fee\s+of\s+(?:USD\s*)?{N}",
        ],
        text,
    )
    b = _first(
        [
            r"rebate\s+of\s+(?:USD\s*)?{N}",                        # "rebate of 24.32 USD"
            r"rebate[^.]*?(?:USD\s*)?{N}",
        ],
        text,
    )
    n = _first(
        [
            r"(?:obtain|receive|get)s?\s+exactly\s+(?:USD\s*)?{N}",  # "obtain exactly 101 USD"
            r"recipient[^.]*?exactly\s+(?:USD\s*)?{N}",
            r"exactly\s+(?:USD\s*)?{N}\s*USD",
        ],
        text,
    )

    retention = 1 - r                                              # proportional-fee retention ratio (A2)

    pre_rebate = n - b                                             # stage 1: remove the rebate (A3, A4)
    after_fee_restore = pre_rebate + f                             # stage 2: restore the fixed fee
    gross = after_fee_restore / retention                          # stage 3: divide by retention ratio

    return {
        "final": gross,
        "slots": {"pre_rebate_checkpoint": pre_rebate},
    }
