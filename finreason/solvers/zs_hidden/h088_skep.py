"""h088 -- merchant batch net settlement (variable fee, fixed fees, unrecovered chargebacks, reserve).

AMBIGUITY HUNT / RESOLUTIONS (all evidence from the question text):

A1. Base of the proportional (variable) fee: gross sales BEFORE chargebacks (G) vs gross net of
    chargebacks (G - C)?
    Text: "gross sales before chargebacks of G ... The processor charges rate r on THOSE gross sales"
    -> "those gross sales" is the just-named gross-before-chargebacks figure. Variable fee = r * G.
    No reduction for chargebacks, recovered or not.

A2. Is "rate 0.04" a ratio or a percent?  Written as "rate 0.04" / "rate 1/28" with no "percent" or
    "%" -> plain ratio, used as-is.  (Defensive: if the token is followed by "percent"/"%", divide by 100.)

A3. Fixed fee base: "plus f per transaction" with the batch having "n transactions" -> fixed fees
    aggregate = f * n.  All n transactions are charged, including those later charged back (nothing
    says chargeback transactions are exempt), and no separate chargeback fee is stated, so none added.

A4. Chargeback loss: "Chargebacks included in the gross-sales amount total C, of which fraction p is
    recovered".  "Included in the gross-sales amount" means the chargeback sales are counted in G, so the
    merchant loses them except for the recovered part.  Unrecovered loss = C * (1 - p)  (equivalently
    C - p*C).  "fraction p" -> plain ratio, not percent (defensive percent handling as in A2).

A5. Reserve: "withholds reserve R" and the net is "after ... reserve" -> R is deducted in full from the
    settlement (it is a withholding, not a fee, but the question explicitly counts it as a deduction).

A6. Net settlement = G - variable_fee - fixed_fees - unrecovered_loss - R.  Gross G is the starting
    point (sales before chargebacks); the chargeback deduction is applied via A4 rather than by starting
    from G - C (which would double count).  No floor at zero is stated, so none applied.

A7. Rounding: "Compute all deductions using exact values" + answer format "round only the final value"
    -> every checkpoint and the final are returned as exact Fractions; the framework rounds each
    independently (half-up, 2 dp).  No intermediate rounding to cents.

A8. Checkpoint identities / units (all usd):
      variable_fee_checkpoint   = r * G            ("the proportional processing fee")
      fixed_fee_checkpoint      = f * n            ("aggregate fixed processing fees")
      chargeback_loss_checkpoint= C * (1 - p)      ("unrecovered chargeback loss")
    All reported as positive deduction amounts (magnitudes), not as negative numbers.
"""

from __future__ import annotations

import re
from fractions import Fraction

from finreason.nums import NUMBER, F, grab  # noqa: F401  (grab kept for parity with contract)

TEMPLATE_ID = "h088"

_MONEY = r"(?:USD\s*|\$\s*)?"  # tolerate an optional currency token before a number


def _num_with_pct(patterns: list[str], text: str) -> Fraction:
    """Match the first pattern that hits; return the captured number as a ratio.

    If the captured number is immediately followed by "percent" or "%", it is divided by 100.
    """
    for pat in patterns:
        rx = pat.replace("{N}", f"({NUMBER})")
        m = re.search(rx, text, flags=re.S | re.I)
        if m is None:
            continue
        val = F(m.group(1))
        tail = text[m.end(1): m.end(1) + 12]
        if re.match(r"\s*(?:percent|%)", tail, flags=re.I):
            val = val / 100
        return val
    raise ValueError(f"none of the patterns matched: {patterns!r}")


def _num(patterns: list[str], text: str) -> Fraction:
    for pat in patterns:
        rx = pat.replace("{N}", f"({NUMBER})")
        m = re.search(rx, text, flags=re.S | re.I)
        if m is not None:
            return F(m.group(1))
    raise ValueError(f"none of the patterns matched: {patterns!r}")


def solve(text: str, q: dict) -> dict:
    # Gross sales before chargebacks and transaction count.
    gross = _num(
        [
            r"gross sales before chargebacks of\s+" + _MONEY + r"{N}",
            r"gross sales of\s+" + _MONEY + r"{N}",
        ],
        text,
    )
    n_tx = _num(
        [
            r"across\s+{N}\s+transactions?",
            r"{N}\s+transactions?",
        ],
        text,
    )

    # Proportional (variable) rate on those gross sales, and per-transaction fixed fee.
    rate = _num_with_pct(
        [
            r"charges\s+(?:a\s+)?rate\s+(?:of\s+)?{N}\s+on those gross sales",
            r"charges\s+(?:a\s+)?rate\s+(?:of\s+)?{N}",
            r"rate\s+(?:of\s+)?{N}\s+on\s+(?:those\s+)?gross sales",
        ],
        text,
    )
    per_tx = _num(
        [
            r"plus\s+" + _MONEY + r"{N}\s+per transaction",
            _MONEY + r"{N}\s+per transaction",
        ],
        text,
    )

    # Chargebacks included in gross sales, and the recovered fraction.
    chargebacks = _num(
        [
            r"Chargebacks included in the gross-sales amount total\s+" + _MONEY + r"{N}",
            r"Chargebacks[^.]*?total\s+" + _MONEY + r"{N}",
        ],
        text,
    )
    recovered_frac = _num_with_pct(
        [
            r"of which\s+(?:a\s+)?fraction\s+(?:of\s+)?{N}\s+is recovered",
            r"fraction\s+(?:of\s+)?{N}\s+is recovered",
            r"of which\s+{N}\s+is recovered",
        ],
        text,
    )

    # Reserve withheld.
    reserve = _num(
        [
            r"withholds\s+(?:a\s+)?reserve\s+(?:of\s+)?" + _MONEY + r"{N}",
            r"reserve\s+(?:of\s+)?" + _MONEY + r"{N}",
        ],
        text,
    )

    # --- exact computation (A1-A6) ---
    variable_fee = rate * gross                      # A1/A2: rate on gross-before-chargebacks
    fixed_fees = per_tx * n_tx                       # A3: per-transaction fee x all transactions
    unrecovered = chargebacks * (Fraction(1) - recovered_frac)  # A4: C * (1 - p)
    net = gross - variable_fee - fixed_fees - unrecovered - reserve  # A5/A6

    return {
        "final": net,
        "slots": {
            "variable_fee_checkpoint": variable_fee,
            "fixed_fee_checkpoint": fixed_fees,
            "chargeback_loss_checkpoint": unrecovered,
        },
    }
