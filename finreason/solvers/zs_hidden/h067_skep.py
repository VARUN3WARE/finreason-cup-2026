"""Cluster h067 -- cash-settled call: premium threshold for a target expiration ROI.

Structure (all amounts per underlying share, USD):
    intrinsic = terminal_price - strike                       (checkpoint, "intrinsic_checkpoint")
    ROI       = (intrinsic - fee - premium) / premium          (simple, non-annualized)
    ROI == target  ==>  premium = (intrinsic - fee) / (1 + target)   (final, USD)

AMBIGUITIES CONSIDERED AND RESOLVED
-----------------------------------
A1. What exactly is the "intrinsic payoff" checkpoint -- before or after the settlement fee?
    Text: "Its intrinsic payoff is terminal price minus strike. Deduct the additional settlement
    fee ..., which is separate from the strike already embedded in that payoff."  The fee is
    deducted *from* the payoff in the ROI formula ("intrinsic payoff minus settlement fee minus
    premium"), so the payoff itself is strike-only: intrinsic = S_T - K, fee NOT subtracted.
    Slot description: "per-share intrinsic payoff" -> S_T - K.
A2. Is intrinsic floored at zero (max(S_T - K, 0))?  The text asserts the call "expires in the
    money" and defines the payoff as "terminal price minus strike", so S_T - K > 0 by premise.
    We implement the stated definition literally (S_T - K); it coincides with max(.,0) whenever
    the stated premise holds.
A3. Target: ratio or percent?  "target ratio 4, where 0.20 means 20%" -- the number is already a
    plain ratio (4 == 400%, 0.25 == 25%).  Used as-is; NOT divided by 100.  (Defensive: if the
    captured number were immediately followed by '%' / 'percent' we would divide by 100, but the
    cluster text never does this.)
A4. Is the premium part of the ROI denominator only, or also subtracted in the numerator?  Text:
    "ROI equals (intrinsic payoff minus settlement fee minus premium) divided by premium" ->
    premium appears in both; hence (I - f - p)/p = t  <=>  p = (I - f)/(1 + t).
A5. Which premium satisfies the threshold -- the exact root or the greatest executable whole-cent
    premium?  Text: "compute the exact premium threshold ... Carry the threshold exactly, then
    report it using half-up rounding to cents. The displayed amount is a rounded report of the
    exact threshold, not necessarily the greatest executable whole-cent premium."  -> return the
    exact rational root; the framework applies half-up rounding to 2 dp.  No floor/ceiling.
A6. Financing / discounting / annualization: explicitly ignored ("Ignore financing and
    discounting", "Simple nonannualized").  No time-value adjustments.
A7. Units: everything is "per underlying share" in USD; answer unit usd, checkpoint unit usd.
    No contract multiplier (e.g. x100) is applied.
A8. Number parsing: all four inputs are anchored on their surrounding words ("terminal stock
    price", "strike price", "settlement fee", "target ratio").  The clause "where 0.20 means 20%"
    contains decoy numbers and is never matched because the target regex anchors right after
    "target ratio".
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h067"


def _first(text: str, patterns: list[str]) -> Fraction:
    """Try several anchored regex patterns (each with one {N}); return the first hit."""
    last_err: Exception | None = None
    for p in patterns:
        try:
            return grab(p, text)
        except ValueError as e:  # pattern not found -> try the next anchor
            last_err = e
    raise ValueError(f"none of the patterns matched: {patterns!r}") from last_err


def _target_ratio(text: str) -> Fraction:
    """Target ROI as a plain ratio (0.25 == 25%)."""
    pats = [
        r"target\s+ratio\s+(?:of\s+|is\s+)?(?:USD\s*)?{N}",
        r"target\s+(?:ROI|return|ratio)[^0-9\-]{0,25}?{N}",
    ]
    for p in pats:
        rx = p.replace("{N}", f"({NUMBER})")
        m = re.search(rx, text, flags=re.S | re.I)
        if m is None:
            continue
        value = F(m.group(1))
        tail = text[m.end(1): m.end(1) + 10]
        # Defensive only: the cluster states a ratio ("where 0.20 means 20%"), so this branch
        # fires solely if an instance wrote the target as an explicit percentage.
        if re.match(r"\s*(?:%|percent)", tail, flags=re.I):
            value /= 100
        return value
    raise ValueError("target ratio not found")


def solve(text: str, q: dict) -> dict:
    terminal = _first(text, [
        r"terminal\s+(?:stock\s+)?price\s+(?:of\s+)?(?:USD\s*)?{N}",
        r"terminal\s+(?:stock\s+)?price[^0-9\-]{0,25}?{N}",
    ])
    strike = _first(text, [
        r"strike\s+price\s+(?:of\s+)?(?:USD\s*)?{N}",
        r"strike[^0-9\-]{0,25}?{N}",
    ])
    fee = _first(text, [
        r"settlement\s+fee\s+(?:of\s+)?(?:USD\s*)?{N}",
        r"settlement\s+fee[^0-9\-]{0,25}?{N}",
    ])
    target = _target_ratio(text)

    # A1/A2: intrinsic payoff = terminal price minus strike (fee NOT deducted here).
    intrinsic = terminal - strike

    # A4/A5: (intrinsic - fee - p) / p = target  ==>  p = (intrinsic - fee) / (1 + target), exact.
    premium = (intrinsic - fee) / (1 + target)

    return {
        "final": premium,
        "slots": {"intrinsic_checkpoint": intrinsic},
    }
