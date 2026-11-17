"""h062 -- FX round-trip with entry/exit fees and a financing charge: solve for the exit quote
that delivers a stated net return.

AMBIGUITIES CONSIDERED AND RESOLVED (textual evidence in brackets):

A1. "retains one minus fee ratio 0.02" -- is 0.02 the FEE ratio (so the conversion keeps 0.98) or
    the retention ratio itself (keeps 0.02)?  The number is attached to the noun phrase "fee ratio",
    and "one minus" is the operator applied to it; every fee value across the three instances
    (0.02, 0.07, 0.2, 0.5, 0.09, 0.03) is fee-sized.  => retention = 1 - fee.

A2. Quote direction.  "expressed as reporting-currency units per base-currency unit": one base unit
    costs Q_e reporting units, so base bought = C / Q_e, and at exit reporting = base * Q_x.  Both quotes
    are stated in the same convention ("normalized exit quote").

A3. Which capital base the fees act on.  Whether the entry fee is taken from the reporting amount before
    conversion or from the base amount after, the result is multiplicative: base_retained =
    C * (1 - f_e) / Q_e.  Same for exit.  No ambiguity in the result.

A4. Financing charge.  "equal to 0.0306153 times the initial reporting-currency capital": an additive
    amount c * C deducted from the exit proceeds -- NOT a proportion of exit proceeds, NOT compounded.

A5. "net return equals 0.18" = (final reporting - C) / C, i.e. profit over capital (standard meaning of
    'return'), not final/C.  => final reporting = (1 + r) * C.

A6. Checkpoint "return-and-carry gross growth multiple" (unit: multiple).  The description names only the
    return and the carry (financing charge), so it is the multiple the retained position must deliver
    before carry: G = 1 + r + c.  It is NOT the fee-adjusted ratio Q_x/Q_e (that would be a quote ratio,
    not a "return-and-carry" multiple).

A7. Rounding.  "Carry all arithmetic exactly" -- nothing is rounded inside the chain; the framework
    applies half-up to six places to the unrounded final and checkpoint.

A8. Capital normalization.  The capital C is never given numerically; every quantity is linear in C,
    so C = 1 is used and the threshold is independent of C.

Derivation (C = 1):
    base          = (1 - f_e) / Q_e
    exit proceeds = base * Q_x * (1 - f_x)
    net return r  = exit proceeds - c - 1
    => Q_x = Q_e * (1 + r + c) / ((1 - f_e) * (1 - f_x))
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab

TEMPLATE_ID = "h062"


def _grab_first(patterns: list[str], text: str) -> Fraction:
    """Try several anchored patterns in order; first hit wins."""
    for p in patterns:
        try:
            return grab(p, text)
        except ValueError:
            continue
    raise ValueError(f"none of the patterns matched: {patterns!r}")


def _fee_values(text: str) -> tuple[Fraction, Fraction]:
    """Entry fee ratio and exit fee ratio.

    Primary: anchor on 'entry conversion ... retains' and on 'At exit ... retain'.
    Fallback: the two 'one minus fee ratio {N}' occurrences in reading order
    (entry is stated before exit in the text).
    """
    entry = None
    exit_ = None
    try:
        entry = grab(r"entry conversion retains one minus fee ratio {N}", text)
    except ValueError:
        pass
    try:
        exit_ = grab(r"At exit.*?retain one minus fee ratio {N}", text)
    except ValueError:
        pass
    if entry is None or exit_ is None:
        rx = re.compile(r"one minus fee ratio\s*(" + NUMBER + r")", re.S)
        found = [F(m.group(1)) for m in rx.finditer(text)]
        if len(found) < 2:
            raise ValueError("could not locate both fee ratios")
        if entry is None:
            entry = found[0]
        if exit_ is None:
            exit_ = found[1]
    return entry, exit_


def solve(text: str, q: dict) -> dict:
    # Entry quote: reporting-currency units per base-currency unit (A2).
    q_entry = _grab_first(
        [
            r"normalized entry quote {N}",
            r"entry quote {N}",
        ],
        text,
    )

    # Fee ratios (A1): the conversions retain (1 - fee).
    fee_entry, fee_exit = _fee_values(text)
    keep_entry = 1 - fee_entry
    keep_exit = 1 - fee_exit

    # Financing charge as a fraction of initial capital (A4).
    carry = _grab_first(
        [
            r"financing charge equal to {N} times the initial reporting-currency capital",
            r"financing charge equal to {N} times",
            r"financing charge[^.]*?{N}",
        ],
        text,
    )

    # Target net return, profit over capital (A5).
    target = _grab_first(
        [
            r"net return equals {N}",
            r"net return (?:equal to|of|is) {N}",
        ],
        text,
    )

    # Checkpoint (A6): gross growth multiple the retained position must achieve before carry.
    gross_growth = 1 + target + carry

    # Exit-quote threshold (derivation in module docstring).
    exit_quote = q_entry * gross_growth / (keep_entry * keep_exit)

    return {
        "final": exit_quote,
        "slots": {"gross_growth_checkpoint": gross_growth},
    }
